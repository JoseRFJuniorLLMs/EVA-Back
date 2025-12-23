from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from ..models import Agendamento, Idoso
from typing import List, Optional
import datetime

class AgendamentoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, agendamento_id: int) -> Optional[Agendamento]:
        query = select(Agendamento).filter(Agendamento.id == agendamento_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100, idoso_id: int = None) -> List[Agendamento]:
        query = select(Agendamento)
        if idoso_id:
            query = query.filter(Agendamento.idoso_id == idoso_id)
        result = await self.db.execute(query.order_by(Agendamento.horario.desc()).offset(skip).limit(limit))
        return result.scalars().all()

    async def create(self, dados: dict) -> Agendamento:
        agendamento = Agendamento(**dados)
        self.db.add(agendamento)
        await self.db.commit()
        await self.db.refresh(agendamento)
        return agendamento

    async def update(self, id: int, dados: dict) -> Optional[Agendamento]:
        agendamento = await self.get_by_id(id)
        if agendamento:
            for k, v in dados.items():
                if v is not None:
                    setattr(agendamento, k, v)
            await self.db.commit()
            await self.db.refresh(agendamento)
        return agendamento

    async def delete(self, id: int) -> bool:
        agendamento = await self.get_by_id(id)
        if agendamento:
            await self.db.delete(agendamento)
            await self.db.commit()
            return True
        return False

    async def update_status(self, agendamento_id: int, status: str) -> Optional[Agendamento]:
        return await self.update(agendamento_id, {'status': status})

    async def get_details_with_idoso(self, agendamento_id: int):
        query = select(Agendamento, Idoso).join(Idoso).filter(Agendamento.id == agendamento_id)
        result = await self.db.execute(query)
        return result.first()

    async def get_pending_calls(self) -> List[Agendamento]:
        now = datetime.datetime.now()
        query = select(Agendamento).filter(
            Agendamento.status == 'pendente',
            Agendamento.horario <= now
        )
        result = await self.db.execute(query)
        return result.scalars().all()