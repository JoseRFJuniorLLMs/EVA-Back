from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from ..models import ProtocoloAlerta, ProtocoloEtapa
from typing import List, Optional

class ProtocoloRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_idoso(self, idoso_id: int) -> List[ProtocoloAlerta]:
        query = select(ProtocoloAlerta).filter(ProtocoloAlerta.idoso_id == idoso_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_active_protocol(self, idoso_id: int) -> Optional[ProtocoloAlerta]:
        query = select(ProtocoloAlerta).filter(
            ProtocoloAlerta.idoso_id == idoso_id,
            ProtocoloAlerta.ativo == True
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_protocolo(self, idoso_id: int, nome: str) -> ProtocoloAlerta:
        protocolo = ProtocoloAlerta(idoso_id=idoso_id, nome=nome)
        self.db.add(protocolo)
        await self.db.commit()
        await self.db.refresh(protocolo)
        return protocolo

    async def add_etapa(self, protocolo_id: int, dados: dict) -> ProtocoloEtapa:
        etapa = ProtocoloEtapa(protocolo_id=protocolo_id, **dados)
        self.db.add(etapa)
        await self.db.commit()
        await self.db.refresh(etapa)
        return etapa

    async def get_etapas(self, protocolo_id: int) -> List[ProtocoloEtapa]:
        query = select(ProtocoloEtapa).filter(ProtocoloEtapa.protocolo_id == protocolo_id).order_by(ProtocoloEtapa.ordem)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def delete_etapa(self, etapa_id: int) -> bool:
        query = select(ProtocoloEtapa).filter(ProtocoloEtapa.id == etapa_id)
        result = await self.db.execute(query)
        etapa = result.scalar_one_or_none()
        if etapa:
            await self.db.delete(etapa)
            await self.db.commit()
            return True
        return False
