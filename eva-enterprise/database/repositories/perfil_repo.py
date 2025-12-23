from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from ..models import IdosoPerfilClinico, IdosoMemoria
from typing import List, Optional

class PerfilRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Perfil Clínico
    async def get_perfil_clinico(self, idoso_id: int) -> Optional[IdosoPerfilClinico]:
        query = select(IdosoPerfilClinico).filter(IdosoPerfilClinico.idoso_id == idoso_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_perfil_clinico(self, idoso_id: int, dados: dict) -> IdosoPerfilClinico:
        perfil = await self.get_perfil_clinico(idoso_id)
        if not perfil:
            perfil = IdosoPerfilClinico(idoso_id=idoso_id, **dados)
            self.db.add(perfil)
        else:
            for k, v in dados.items():
                setattr(perfil, k, v)
        
        await self.db.commit()
        await self.db.refresh(perfil)
        return perfil

    # Memória
    async def get_memorias(self, idoso_id: int, categoria: str = None) -> List[IdosoMemoria]:
        query = select(IdosoMemoria).filter(IdosoMemoria.idoso_id == idoso_id)
        if categoria:
            query = query.filter(IdosoMemoria.categoria == categoria)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def add_memoria(self, idoso_id: int, categoria: str, chave: str, valor: str, relevancia: str = 'media') -> IdosoMemoria:
        memoria = IdosoMemoria(idoso_id=idoso_id, categoria=categoria, chave=chave, valor=valor, relevancia=relevancia)
        self.db.add(memoria)
        await self.db.commit()
        await self.db.refresh(memoria)
        return memoria

    async def delete_memoria(self, memoria_id: int) -> bool:
        query = select(IdosoMemoria).filter(IdosoMemoria.id == memoria_id)
        result = await self.db.execute(query)
        memoria = result.scalar_one_or_none()
        if memoria:
            await self.db.delete(memoria)
            await self.db.commit()
            return True
        return False
