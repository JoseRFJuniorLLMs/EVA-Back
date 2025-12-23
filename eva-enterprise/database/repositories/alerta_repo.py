from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from ..models import Alerta, PsicologiaInsight, TopicoAfetivo
from typing import List, Optional
import datetime

class AlertaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_recent_alerts(self, limit: int = 50, tipo: str = None) -> List[Alerta]:
        query = select(Alerta)
        if tipo:
            query = query.filter(Alerta.tipo == tipo)
        result = await self.db.execute(query.order_by(Alerta.criado_em.desc()).limit(limit))
        return result.scalars().all()

    async def create_alerta(self, tipo: str, descricao: str) -> Alerta:
        alerta = Alerta(tipo=tipo, descricao=descricao)
        self.db.add(alerta)
        await self.db.commit()
        await self.db.refresh(alerta)
        return alerta

    async def get_by_id(self, id: int) -> Optional[Alerta]:
        query = select(Alerta).filter(Alerta.id == id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def resolve_alerta(self, id: int) -> Optional[Alerta]:
        alerta = await self.get_by_id(id)
        if alerta:
            alerta.status = 'resolvido'
            await self.db.commit()
            await self.db.refresh(alerta)
        return alerta

    # Insights
    async def get_insights(self, idoso_id: int) -> List[PsicologiaInsight]:
        query = select(PsicologiaInsight).filter(PsicologiaInsight.idoso_id == idoso_id).order_by(PsicologiaInsight.data_geracao.desc())
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_insight(self, idoso_id: int, conteudo: str, relevancia: int) -> PsicologiaInsight:
        insight = PsicologiaInsight(idoso_id=idoso_id, conteudo=conteudo, relevancia=relevancia)
        self.db.add(insight)
        await self.db.commit()
        await self.db.refresh(insight)
        return insight

    # Topicos Afetivos
    async def get_topicos(self, idoso_id: int) -> List[TopicoAfetivo]:
        query = select(TopicoAfetivo).filter(TopicoAfetivo.idoso_id == idoso_id).order_by(TopicoAfetivo.frequencia.desc())
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_topico(self, idoso_id: int, topico: str) -> TopicoAfetivo:
        query = select(TopicoAfetivo).filter(
            TopicoAfetivo.idoso_id == idoso_id,
            TopicoAfetivo.topico == topico
        )
        result = await self.db.execute(query)
        existing = result.scalar_one_or_none()

        if existing:
            existing.frequencia += 1
            existing.ultima_mencao = datetime.datetime.now()
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            new_topic = TopicoAfetivo(idoso_id=idoso_id, topico=topico)
            self.db.add(new_topic)
            await self.db.commit()
            await self.db.refresh(new_topic)
            return new_topic
