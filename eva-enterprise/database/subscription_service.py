from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from database.models import AssinaturaEntidade
from schemas import SubscriptionCreate, SubscriptionUpdate
from datetime import datetime
from typing import Optional, List

# Mapeamento de features por plano
PLAN_FEATURES = {
    "livre": {
        "interface_acessivel": True,
        "cadastro_idoso": True,
        "historico_chamadas": True,
        "ligar_agora_manual": True,
        "lembretes_automaticos": False,
        "confirmacao_medicacao": False,
        "personalizacao_audio": False,
        "alertas_nao_atendeu": False,
        "deteccao_emergencias": False,
        "monitoramento_tempo_real": False,
        "relatorios_detalhados": False,
        "ia_avancada": False,
        "api_integracao": False,
        "suporte_prioritario": False,
    },
    "essencial": {
        "interface_acessivel": True,
        "cadastro_idoso": True,
        "historico_chamadas": True,
        "ligar_agora_manual": True,
        "lembretes_automaticos": True,
        "confirmacao_medicacao": True,
        "personalizacao_audio": True,
        "alertas_nao_atendeu": True,
        "deteccao_emergencias": False,
        "monitoramento_tempo_real": False,
        "relatorios_detalhados": False,
        "ia_avancada": False,
        "api_integracao": False,
        "suporte_prioritario": False,
    },
    "familia_plus": {
        "interface_acessivel": True,
        "cadastro_idoso": True,
        "historico_chamadas": True,
        "ligar_agora_manual": True,
        "lembretes_automaticos": True,
        "confirmacao_medicacao": True,
        "personalizacao_audio": True,
        "alertas_nao_atendeu": True,
        "deteccao_emergencias": True,
        "monitoramento_tempo_real": True,
        "relatorios_detalhados": True,
        "ia_avancada": True,
        "api_integracao": False,
        "suporte_prioritario": False,
    },
    "profissional": {
        "interface_acessivel": True,
        "cadastro_idoso": True,
        "historico_chamadas": True,
        "ligar_agora_manual": True,
        "lembretes_automaticos": True,
        "confirmacao_medicacao": True,
        "personalizacao_audio": True,
        "alertas_nao_atendeu": True,
        "deteccao_emergencias": True,
        "monitoramento_tempo_real": True,
        "relatorios_detalhados": True,
        "ia_avancada": True,
        "idosos_ilimitados": True,
        "integracao_sensores": True,
        "lembretes_consultas": True,
        "hipaa_ready": True,
        "api_integracao": True,
        "suporte_prioritario": True,
    },
}


class SubscriptionService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_all(self) -> List[AssinaturaEntidade]:
        """Retorna todas as assinaturas"""
        result = await self.db.execute(select(AssinaturaEntidade))
        return result.scalars().all()
    
    async def get_by_id(self, id: int) -> Optional[AssinaturaEntidade]:
        """Busca assinatura por ID"""
        result = await self.db.execute(
            select(AssinaturaEntidade).where(AssinaturaEntidade.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_active_by_entity(self, entity_name: str) -> Optional[AssinaturaEntidade]:
        """Busca assinatura ativa por nome da entidade"""
        result = await self.db.execute(
            select(AssinaturaEntidade).where(
                AssinaturaEntidade.entidade_nome == entity_name,
                AssinaturaEntidade.status == "ativo"
            )
        )
        return result.scalar_one_or_none()
    
    async def create(self, data: SubscriptionCreate) -> AssinaturaEntidade:
        """Cria nova assinatura"""
        sub = AssinaturaEntidade(**data.dict())
        self.db.add(sub)
        await self.db.commit()
        await self.db.refresh(sub)
        return sub
    
    async def update(self, id: int, data: SubscriptionUpdate) -> Optional[AssinaturaEntidade]:
        """Atualiza assinatura"""
        sub = await self.get_by_id(id)
        if not sub:
            return None
        
        update_data = data.dict(exclude_unset=True)
        update_data["atualizado_em"] = datetime.utcnow()
        
        await self.db.execute(
            update(AssinaturaEntidade)
            .where(AssinaturaEntidade.id == id)
            .values(**update_data)
        )
        await self.db.commit()
        return await self.get_by_id(id)
    
    async def update_status(self, id: int, status: str) -> Optional[dict]:
        """Atualiza status da assinatura"""
        sub = await self.get_by_id(id)
        if not sub:
            return None
        
        await self.db.execute(
            update(AssinaturaEntidade)
            .where(AssinaturaEntidade.id == id)
            .values(status=status, atualizado_em=datetime.utcnow())
        )
        await self.db.commit()
        return {"message": "Status atualizado com sucesso", "status": status}
    
    async def delete(self, id: int) -> bool:
        """Exclui assinatura"""
        sub = await self.get_by_id(id)
        if not sub:
            return False
        
        await self.db.execute(
            delete(AssinaturaEntidade).where(AssinaturaEntidade.id == id)
        )
        await self.db.commit()
        return True
    
    async def get_features(self, id: int) -> Optional[dict]:
        """Retorna features do plano da assinatura"""
        sub = await self.get_by_id(id)
        if not sub:
            return None
        return PLAN_FEATURES.get(sub.plano_id, {})
    
    async def check_feature(self, entity_name: str, feature: str) -> bool:
        """Verifica se entidade tem acesso a uma feature específica"""
        sub = await self.get_active_by_entity(entity_name)
        if not sub:
            return False
        features = PLAN_FEATURES.get(sub.plano_id, {})
        return features.get(feature, False)
    
    async def get_usage(self, id: int) -> Optional[dict]:
        """Retorna estatísticas de uso de minutos"""
        sub = await self.get_by_id(id)
        if not sub:
            return None
        return {
            "minutos_consumidos": sub.minutos_consumidos,
            "limite_minutos": sub.limite_minutos,
            "minutos_restantes": sub.limite_minutos - sub.minutos_consumidos,
            "percentual_usado": round((sub.minutos_consumidos / sub.limite_minutos) * 100, 2) if sub.limite_minutos > 0 else 0
        }
    
    async def consume_minutes(self, id: int, minutes: int) -> dict:
        """Registra consumo de minutos"""
        sub = await self.get_by_id(id)
        if not sub:
            raise ValueError("Assinatura não encontrada")
        
        new_consumed = sub.minutos_consumidos + minutes
        if new_consumed > sub.limite_minutos:
            raise ValueError(
                f"Limite de minutos excedido: tentando consumir {minutes} minutos, "
                f"mas restam apenas {sub.limite_minutos - sub.minutos_consumidos} minutos"
            )
        
        await self.db.execute(
            update(AssinaturaEntidade)
            .where(AssinaturaEntidade.id == id)
            .values(minutos_consumidos=new_consumed, atualizado_em=datetime.utcnow())
        )
        await self.db.commit()
        return await self.get_usage(id)
