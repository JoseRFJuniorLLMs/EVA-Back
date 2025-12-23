from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from ..models import Idoso, Familiar, LegadoDigital
from typing import List, Optional

class IdosoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, skip: int = 0, limit: int = 100, nome: str = None, cpf: str = None, telefone: str = None) -> List[Idoso]:
        query = select(Idoso)
        if nome:
            query = query.filter(Idoso.nome.ilike(f"%{nome}%"))
        if cpf:
            query = query.filter(Idoso.cpf.contains(cpf))
        if telefone:
            query = query.filter(Idoso.telefone.contains(telefone))
        
        result = await self.db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()

    async def get_by_id(self, idoso_id: int) -> Optional[Idoso]:
        query = select(Idoso).filter(Idoso.id == idoso_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_telefone(self, telefone: str) -> Optional[Idoso]:
        query = select(Idoso).filter(Idoso.telefone == telefone)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create(self, dados: dict) -> Idoso:
        idoso = Idoso(**dados)
        self.db.add(idoso)
        await self.db.commit()
        await self.db.refresh(idoso)
        return idoso

    async def update(self, idoso_id: int, dados: dict) -> Optional[Idoso]:
        idoso = await self.get_by_id(idoso_id)
        if idoso:
            for k, v in dados.items():
                if v is not None:
                    setattr(idoso, k, v)
            await self.db.commit()
            await self.db.refresh(idoso)
        return idoso

    async def delete(self, idoso_id: int) -> bool:
        idoso = await self.get_by_id(idoso_id)
        if idoso:
            await self.db.delete(idoso)
            await self.db.commit()
            return True
        return False

    # Familiares
    async def get_familiares(self, idoso_id: int) -> List[Familiar]:
        query = select(Familiar).filter(Familiar.idoso_id == idoso_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def add_familiar(self, idoso_id: int, dados: dict) -> Familiar:
        familiar = Familiar(idoso_id=idoso_id, **dados)
        self.db.add(familiar)
        await self.db.commit()
        await self.db.refresh(familiar)
        return familiar

    async def update_familiar(self, familiar_id: int, dados: dict) -> Optional[Familiar]:
        query = select(Familiar).filter(Familiar.id == familiar_id)
        result = await self.db.execute(query)
        familiar = result.scalar_one_or_none()
        if familiar:
            for k, v in dados.items():
                if v is not None:
                    setattr(familiar, k, v)
            await self.db.commit()
            await self.db.refresh(familiar)
        return familiar

    # Legado Digital
    async def get_legado(self, idoso_id: int) -> List[LegadoDigital]:
        query = select(LegadoDigital).filter(LegadoDigital.idoso_id == idoso_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def add_legado(self, idoso_id: int, dados: dict) -> LegadoDigital:
        item = LegadoDigital(idoso_id=idoso_id, **dados)
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def remove_legado(self, item_id: int) -> bool:
        query = select(LegadoDigital).filter(LegadoDigital.id == item_id)
        result = await self.db.execute(query)
        item = result.scalar_one_or_none()
        if item:
            await self.db.delete(item)
            await self.db.commit()
            return True
        return False
