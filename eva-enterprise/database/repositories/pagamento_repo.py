from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models import Pagamento, AuditLog
from typing import List, Optional
import datetime

class PagamentoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_pagamentos(self, limit: int = 50, status: str = None) -> List[Pagamento]:
        query = select(Pagamento)
        if status:
            query = query.filter(Pagamento.status == status)
        result = await self.db.execute(query.order_by(Pagamento.data.desc()).limit(limit))
        return result.scalars().all()

    async def create_pagamento(self, dados: dict) -> Pagamento:
        pagamento = Pagamento(**dados)
        self.db.add(pagamento)
        await self.db.commit()
        await self.db.refresh(pagamento)
        return pagamento

    async def get_by_id(self, id: int) -> Optional[Pagamento]:
        query = select(Pagamento).filter(Pagamento.id == id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

class AuditRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_action(self, acao: str, usuario: str, detalhes: dict) -> AuditLog:
        log = AuditLog(acao=acao, usuario=usuario, detalhes=detalhes)
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def get_logs(self, limit: int = 100, usuario: str = None) -> List[AuditLog]:
        query = select(AuditLog)
        if usuario:
            query = query.filter(AuditLog.usuario == usuario)
        result = await self.db.execute(query.order_by(AuditLog.data.desc()).limit(limit))
        return result.scalars().all()

    async def get_by_id(self, id: int) -> Optional[AuditLog]:
        query = select(AuditLog).filter(AuditLog.id == id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
