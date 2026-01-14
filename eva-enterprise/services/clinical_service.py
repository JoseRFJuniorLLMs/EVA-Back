from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from database.models import (
    Medicamento, 
    CatalogoFarmaceutico, 
    InteracoesRisco, 
    ReferenciaDosagem,
    RiscosGeriatricos,
    Idoso,
    IdosoPerfilClinico
)
import re
from typing import List, Dict, Optional

class ClinicalService:
    """
    Serviço de Inteligência Clínica Farmacêutica.
    Responsável por validar segurança, interações e riscos geriátricos.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def check_interactions(self, idoso_id: int, new_catalogo_id: int) -> List[Dict]:
        """
        Verifica interações medicamentosas entre o novo medicamento e os já em uso.
        """
        # 1. Buscar medicamentos ativos do idoso
        result = await self.db.execute(
            select(Medicamento)
            .where(Medicamento.idoso_id == idoso_id)
            .where(Medicamento.ativo == True)
            .where(Medicamento.catalogo_ref_id.isnot(None))
        )
        current_meds = result.scalars().all()
        
        if not current_meds:
            return []

        current_catalogo_ids = [med.catalogo_ref_id for med in current_meds]
        
        # 2. Buscar interações na base de conhecimento (bidirecional)
        query = select(InteracoesRisco).where(
            or_(
                and_(
                    InteracoesRisco.catalogo_id_a == new_catalogo_id,
                    InteracoesRisco.catalogo_id_b.in_(current_catalogo_ids)
                ),
                and_(
                    InteracoesRisco.catalogo_id_b == new_catalogo_id,
                    InteracoesRisco.catalogo_id_a.in_(current_catalogo_ids)
                )
            )
        )
        
        result_interactions = await self.db.execute(query)
        interactions = result_interactions.scalars().all()
        
        alerts = []
        for interaction in interactions:
            # Identificar qual é o medicamento conflitante que o idoso já toma
            other_id = interaction.catalogo_id_b if interaction.catalogo_id_a == new_catalogo_id else interaction.catalogo_id_a
            
            # Buscar nome do medicamento conflitante
            conflicting_med_name = next(
                (med.nome for med in current_meds if med.catalogo_ref_id == other_id), 
                "Medicamento Desconhecido"
            )
            
            alerts.append({
                "type": "interaction",
                "severity": interaction.nivel_perigo, # FATAL, ALTO, MEDIO
                "message": f"Interação detectada com {conflicting_med_name}: {interaction.mensagem_alerta}",
                "description": interaction.descricao,
                "management": interaction.manejo_clinico
            })
            
        return alerts

    async def validate_dosage(self, catalogo_id: int, dosage_str: str) -> List[Dict]:
        """
        Valida se a dosagem informada está dentro dos limites seguros.
        """
        if not dosage_str:
            return []

        # 1. Buscar referência de dosagem
        result = await self.db.execute(
            select(ReferenciaDosagem).where(ReferenciaDosagem.catalogo_id == catalogo_id)
        )
        ref = result.scalar_one_or_none()
        
        if not ref or not ref.dose_maxima_mg:
            return []

        # 2. Extrair valor numérico da string (ex: "500mg" -> 500)
        # Regex simples para pegar o primeiro número encontrado
        match = re.search(r'(\d+(?:\.\d+)?)', dosage_str)
        if not match:
            return []
        
        try:
            dose_value = float(match.group(1))
        except ValueError:
            return []
            
        alerts = []
        
        # TODO: A lógica aqui assume que dosage_str é a dose diária ou única? 
        # Idealmente precisaria saber a frequência. Por precaução, vamos alertar sobre dose única alta.
        
        if dose_value > float(ref.dose_maxima_mg):
            alerts.append({
                "type": "dosage",
                "severity": "ALTO",
                "message": f"Dose informada ({dose_value}mg) excede o máximo recomendado ({ref.dose_maxima_mg}mg).",
                "details": f"Alerta Renal: {ref.alerta_renal}" if ref.alerta_renal else None
            })
            
        return alerts

    async def analyze_geriatric_risk(self, idoso_id: int, catalogo_id: int) -> List[Dict]:
        """
        Analisa riscos específicos para idosos (Critérios de Beers / STOPP/START).
        """
        alerts = []
        
        # 1. Buscar dados do risco geriátrico para o medicamento
        result_risk = await self.db.execute(
            select(RiscosGeriatricos).where(RiscosGeriatricos.catalogo_id == catalogo_id)
        )
        risk_profile = result_risk.scalar_one_or_none()
        
        if not risk_profile:
            return []
            
        # 2. Buscar perfil do idoso
        result_idoso = await self.db.execute(
            select(Idoso).where(Idoso.id == idoso_id)
        )
        idoso = result_idoso.scalar_one_or_none()
        
        if not idoso:
            return []

        # 3. Cruzamento de dados
        
        # Risco de Queda
        if risk_profile.risco_queda:
            # Se idoso tem mobilidade reduzida ou histórico
            if idoso.mobilidade in ['auxiliado', 'cadeira_rodas', 'acamado']:
                alerts.append({
                    "type": "geriatric_risk",
                    "severity": "ALTO",
                    "risk": "Risco de Queda Aumentado",
                    "message": "Este medicamento aumenta risco de quedas em paciente com mobilidade reduzida."
                })
        
        # Confusão Mental / Demência
        if risk_profile.confusao_mental or risk_profile.agravamento_demencia:
            if idoso.nivel_cognitivo in ['moderado', 'severo']:
                 alerts.append({
                    "type": "geriatric_risk",
                    "severity": "ALTO",
                    "risk": "Agravamento Cognitivo",
                    "message": "Pode piorar quadro de confusão mental ou demência existente."
                })

        # Alerta Geral se houver observações importantes
        if risk_profile.observacoes:
             alerts.append({
                    "type": "geriatric_info",
                    "severity": "MEDIO",
                    "risk": "Observação Geriátrica",
                    "message": risk_profile.observacoes
                })
                
        return alerts

    async def full_safety_check(self, idoso_id: int, catalogo_id: int, dosage: str = None) -> Dict:
        """
        Executa todas as verificações de segurança de uma vez.
        """
        
        interactions = await self.check_interactions(idoso_id, catalogo_id)
        geriatric_risks = await self.analyze_geriatric_risk(idoso_id, catalogo_id)
        dosage_alerts = await self.validate_dosage(catalogo_id, dosage) if dosage else []
        
        all_alerts = interactions + geriatric_risks + dosage_alerts
        
        # Determina status geral
        status = "safe"
        if any(a['severity'] in ['FATAL', 'ALTO'] for a in all_alerts):
            status = "danger"
        elif all_alerts:
            status = "warning"
            
        return {
            "status": status,
            "alerts": all_alerts,
            "summary": f"{len(all_alerts)} alertas encontrados."
        }
