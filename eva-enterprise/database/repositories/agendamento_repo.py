from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from ..models import Agendamento, Idoso
from typing import List, Optional
import datetime

class AgendamentoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, agendamento_id: int) -> Optional[Agendamento]:
        query = select(Agendamento, Idoso.nome.label("idoso_nome"), Idoso.foto_url, Idoso.telefone).join(Idoso, Agendamento.idoso_id == Idoso.id).filter(Agendamento.id == agendamento_id)
        result = await self.db.execute(query)
        row = result.first()
        if row:
            ag = row.Agendamento
            ag.idoso_nome = row.idoso_nome
            ag.foto_url = row.foto_url
            ag.telefone = row.telefone
            return ag
        return None

    async def get_all(self, skip: int = 0, limit: int = 100, idoso_id: int = None) -> List[Agendamento]:
        query = select(Agendamento, Idoso.nome.label("idoso_nome"), Idoso.foto_url, Idoso.telefone).join(Idoso, Agendamento.idoso_id == Idoso.id)
        if idoso_id:
            query = query.filter(Agendamento.idoso_id == idoso_id)
        result = await self.db.execute(query.order_by(Agendamento.data_hora_agendada.desc()).offset(skip).limit(limit))
        
        agendamentos = []
        for row in result:
            ag = row.Agendamento
            ag.idoso_nome = row.idoso_nome
            ag.foto_url = row.foto_url
            ag.telefone = row.telefone
            agendamentos.append(ag)
        return agendamentos

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
            Agendamento.status.in_(['agendado', 'aguardando_retry']),
            Agendamento.data_hora_agendada <= now
        )
        result = await self.db.execute(query)
        return result.scalars().all()