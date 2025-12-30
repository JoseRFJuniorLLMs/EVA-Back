from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_
from database.models import (
    PadraoComportamento,
    PredicaoEmergencia,
    PsicologiaInsight,
    TopicoAfetivo,
    Idoso,
    HistoricoLigacao
)
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import json

class IAService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ==================== IDOSOS ====================
    
    async def get_idoso(self, idoso_id: int):
        """Busca idoso por ID"""
        result = await self.db.execute(
            select(Idoso).where(Idoso.id == idoso_id)
        )
        return result.scalar_one_or_none()
    
    # ==================== PADRÕES DE COMPORTAMENTO ====================
    
    async def get_padroes(
        self, 
        idoso_id: int, 
        ativo: Optional[bool] = None,
        offset: int = 0,
        limit: int = 10
    ) -> tuple[List, int]:
        """Lista padrões de comportamento com paginação"""
        query = select(PadraoComportamento).where(
            PadraoComportamento.idoso_id == idoso_id
        )
        
        if ativo is not None:
            query = query.where(PadraoComportamento.ativo == ativo)
        
        query = query.order_by(PadraoComportamento.confianca.desc())
        
        # Contar total
        from sqlalchemy import func
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0
        
        # Aplicar paginação
        query = query.offset(offset).limit(limit)
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        return items, total
    
    async def get_padrao_by_id(self, id: int):
        """Busca padrão por ID"""
        result = await self.db.execute(
            select(PadraoComportamento).where(PadraoComportamento.id == id)
        )
        return result.scalar_one_or_none()
    
    async def desativar_padrao(self, id: int) -> bool:
        """Desativa um padrão"""
        padrao = await self.get_padrao_by_id(id)
        if not padrao:
            return False
        
        await self.db.execute(
            update(PadraoComportamento)
            .where(PadraoComportamento.id == id)
            .values(ativo=False, atualizado_em=datetime.utcnow())
        )
        await self.db.commit()
        return True
    
    # ==================== PREDIÇÕES DE EMERGÊNCIA ====================
    
    async def get_predicoes(
        self, 
        idoso_id: int, 
        ativas: Optional[bool] = None,
        offset: int = 0,
        limit: int = 10
    ) -> tuple[List, int]:
        """Lista predições de emergência com paginação"""
        query = select(PredicaoEmergencia).where(
            PredicaoEmergencia.idoso_id == idoso_id
        )
        
        if ativas:
            # Predições ativas: não expiradas e não confirmadas como falso positivo
            query = query.where(
                and_(
                    or_(
                        PredicaoEmergencia.validade_ate.is_(None),
                        PredicaoEmergencia.validade_ate > datetime.utcnow()
                    ),
                    PredicaoEmergencia.falso_positivo == False
                )
            )
        
        query = query.order_by(PredicaoEmergencia.probabilidade.desc())
        
        # Contar total
        from sqlalchemy import func
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0
        
        # Aplicar paginação
        query = query.offset(offset).limit(limit)
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        return items, total
    
    async def get_predicao_by_id(self, id: int):
        """Busca predição por ID"""
        result = await self.db.execute(
            select(PredicaoEmergencia).where(PredicaoEmergencia.id == id)
        )
        return result.scalar_one_or_none()
    
    async def confirmar_predicao(self, id: int, confirmada: bool):
        """Confirma ou marca como falso positivo"""
        predicao = await self.get_predicao_by_id(id)
        if not predicao:
            return None
        
        await self.db.execute(
            update(PredicaoEmergencia)
            .where(PredicaoEmergencia.id == id)
            .values(
                confirmada=confirmada,
                falso_positivo=not confirmada,
                data_confirmacao=datetime.utcnow()
            )
        )
        await self.db.commit()
        
        return await self.get_predicao_by_id(id)
    
    # ==================== EMOÇÕES ====================
    
    async def get_historico_chamada(self, ligacao_id: int):
        """Busca histórico de chamada"""
        result = await self.db.execute(
            select(HistoricoLigacao).where(HistoricoLigacao.id == ligacao_id)
        )
        return result.scalar_one_or_none()
    
    async def analisar_emocao_texto(self, transcricao: str, sentimento_geral: str) -> Dict:
        """
        Analisa emoção baseado em transcrição e sentimento.
        Versão simplificada - pode ser melhorada com IA real.
        """
        if not transcricao or not sentimento_geral:
            return {
                "emocao": "neutro",
                "intensidade": 0.5,
                "confianca": 0.3
            }
        
        # Mapeamento simples de sentimento para emoção
        emocao_map = {
            "positivo": "feliz",
            "negativo": "triste",
            "neutro": "neutro",
            "ansioso": "ansioso",
            "confuso": "confuso"
        }
        
        emocao = emocao_map.get(sentimento_geral.lower(), "neutro")
        
        # Calcular intensidade baseado em palavras-chave
        palavras_intensas = ["muito", "demais", "extremamente", "bastante"]
        intensidade = 0.5
        
        for palavra in palavras_intensas:
            if palavra in transcricao.lower():
                intensidade = min(intensidade + 0.2, 1.0)
        
        return {
            "emocao": emocao,
            "intensidade": intensidade,
            "confianca": 0.7,
            "detalhes": {
                "sentimento_original": sentimento_geral,
                "tamanho_transcricao": len(transcricao)
            }
        }
    
    async def get_historico_emocoes(self, idoso_id: int, dias: int = 30) -> List:
        """Retorna histórico de emoções das chamadas"""
        data_limite = datetime.utcnow() - timedelta(days=dias)
        
        query = select(HistoricoLigacao).where(
            and_(
                HistoricoLigacao.idoso_id == idoso_id,
                HistoricoLigacao.inicio_chamada >= data_limite,
                HistoricoLigacao.sentimento_geral.isnot(None)
            )
        ).order_by(HistoricoLigacao.inicio_chamada.desc())
        
        result = await self.db.execute(query)
        chamadas = result.scalars().all()
        
        # Converter para formato de emoção
        emocoes = []
        for chamada in chamadas:
            emocao_data = await self.analisar_emocao_texto(
                chamada.transcricao_resumo or "",
                chamada.sentimento_geral or "neutro"
            )
            emocoes.append({
                "id": chamada.id,
                "data": chamada.inicio_chamada,
                "emocao": emocao_data["emocao"],
                "intensidade": emocao_data["intensidade"],
                "sentimento_original": chamada.sentimento_geral
            })
        
        return emocoes
    
    def calcular_emocao_predominante(self, emocoes: List) -> str:
        """Calcula emoção predominante em uma lista"""
        if not emocoes:
            return "neutro"
        
        # Contar frequência de cada emoção
        contagem = {}
        for emocao in emocoes:
            tipo = emocao.get("emocao", "neutro")
            contagem[tipo] = contagem.get(tipo, 0) + 1
        
        # Retornar a mais frequente
        return max(contagem, key=contagem.get) if contagem else "neutro"
    
    # ==================== INSIGHTS PSICOLÓGICOS ====================
    
    async def get_insights(self, idoso_id: int, tipo: Optional[str] = None) -> List:
        """Lista insights psicológicos"""
        query = select(PsicologiaInsight).where(
            PsicologiaInsight.idoso_id == idoso_id
        )
        
        if tipo:
            query = query.where(PsicologiaInsight.tipo == tipo)
        
        query = query.order_by(PsicologiaInsight.data_insight.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def gerar_insights_ia(self, idoso_id: int) -> List:
        """
        Gera insights baseados em padrões e histórico.
        Versão simplificada - pode ser melhorada com IA real.
        """
        insights = []
        
        # Buscar padrões ativos
        padroes = await self.get_padroes(idoso_id, ativo=True)
        
        # Gerar insights baseados em padrões
        for padrao in padroes:
            if padrao.tipo_padrao == "humor_negativo" and padrao.confianca > 0.6:
                insight = PsicologiaInsight(
                    idoso_id=idoso_id,
                    tipo="alerta",
                    mensagem=f"Padrão de humor negativo detectado: {padrao.descricao}",
                    relevancia="alta",
                    conteudo=json.dumps({
                        "padrao_id": padrao.id,
                        "confianca": float(padrao.confianca)
                    })
                )
                self.db.add(insight)
                insights.append(insight)
            
            elif padrao.tipo_padrao == "humor_positivo" and padrao.confianca > 0.7:
                insight = PsicologiaInsight(
                    idoso_id=idoso_id,
                    tipo="positivo",
                    mensagem=f"Padrão positivo identificado: {padrao.descricao}",
                    relevancia="media",
                    conteudo=json.dumps({
                        "padrao_id": padrao.id,
                        "confianca": float(padrao.confianca)
                    })
                )
                self.db.add(insight)
                insights.append(insight)
        
        # Buscar predições de alto risco
        predicoes = await self.get_predicoes(idoso_id, ativas=True)
        for predicao in predicoes:
            if predicao.nivel_risco in ["alto", "critico"]:
                insight = PsicologiaInsight(
                    idoso_id=idoso_id,
                    tipo="alerta",
                    mensagem=f"Risco de {predicao.tipo_emergencia} detectado",
                    relevancia="alta",
                    conteudo=json.dumps({
                        "predicao_id": predicao.id,
                        "probabilidade": float(predicao.probabilidade),
                        "nivel_risco": predicao.nivel_risco
                    })
                )
                self.db.add(insight)
                insights.append(insight)
        
        await self.db.commit()
        
        return insights
