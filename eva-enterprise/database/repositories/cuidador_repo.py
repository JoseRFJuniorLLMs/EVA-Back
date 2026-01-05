from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from database.models import Cuidador
from typing import List, Optional


class CuidadorRepository:
    """Repository para operações CRUD da tabela cuidadores"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 10,
        idoso_id: Optional[int] = None,
        tipo_cuidador: Optional[str] = None,
        ativo: Optional[bool] = True
    ) -> List[Cuidador]:
        """Lista cuidadores com filtros opcionais"""
        query = select(Cuidador)
        
        filters = []
        if ativo is not None:
            filters.append(Cuidador.ativo == ativo)
        if idoso_id:
            filters.append(Cuidador.idoso_id == idoso_id)
        if tipo_cuidador:
            filters.append(Cuidador.tipo_cuidador == tipo_cuidador)
        
        if filters:
            query = query.where(and_(*filters))
        
        query = query.offset(skip).limit(limit).order_by(Cuidador.prioridade, Cuidador.id)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_by_id(self, id: int) -> Optional[Cuidador]:
        """Busca cuidador por ID"""
        result = await self.db.execute(
            select(Cuidador).where(Cuidador.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_cpf(self, cpf: str) -> Optional[Cuidador]:
        """Busca cuidador por CPF (aceita formatado ou não)"""
        # Remove formatação do CPF
        cpf_clean = ''.join(filter(str.isdigit, cpf))
        
        # Busca por CPF contendo os dígitos
        result = await self.db.execute(
            select(Cuidador).where(Cuidador.cpf.like(f'%{cpf_clean}%'))
        )
        return result.scalar_one_or_none()
    
    async def get_by_idoso(self, idoso_id: int, ativo: Optional[bool] = True) -> List[Cuidador]:
        """Lista todos os cuidadores de um idoso específico"""
        query = select(Cuidador).where(Cuidador.idoso_id == idoso_id)
        
        if ativo is not None:
            query = query.where(Cuidador.ativo == ativo)
        
        query = query.order_by(Cuidador.prioridade, Cuidador.id)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_emergencia_contacts(self, idoso_id: int) -> List[Cuidador]:
        """Retorna contatos de emergência ordenados por prioridade"""
        result = await self.db.execute(
            select(Cuidador).where(
                and_(
                    Cuidador.idoso_id == idoso_id,
                    Cuidador.eh_contato_emergencia == True,
                    Cuidador.ativo == True
                )
            ).order_by(Cuidador.prioridade, Cuidador.id)
        )
        return result.scalars().all()
    
    async def get_responsavel(self, idoso_id: int) -> Optional[Cuidador]:
        """Retorna o responsável legal do idoso"""
        result = await self.db.execute(
            select(Cuidador).where(
                and_(
                    Cuidador.idoso_id == idoso_id,
                    Cuidador.eh_responsavel == True,
                    Cuidador.ativo == True
                )
            ).order_by(Cuidador.prioridade).limit(1)
        )
        return result.scalar_one_or_none()
    
    async def create(self, data: dict) -> Cuidador:
        """Cria novo cuidador"""
        cuidador = Cuidador(**data)
        self.db.add(cuidador)
        await self.db.commit()
        await self.db.refresh(cuidador)
        return cuidador
    
    async def update(self, id: int, data: dict) -> Optional[Cuidador]:
        """Atualiza cuidador existente"""
        cuidador = await self.get_by_id(id)
        if not cuidador:
            return None
        
        for key, value in data.items():
            if hasattr(cuidador, key):
                setattr(cuidador, key, value)
        
        await self.db.commit()
        await self.db.refresh(cuidador)
        return cuidador
    
    async def update_device_token(self, id: int, token: str) -> bool:
        """Atualiza apenas o device_token"""
        cuidador = await self.get_by_id(id)
        if not cuidador:
            return False
        
        cuidador.device_token = token
        await self.db.commit()
        return True
    
    async def update_token_by_cpf(self, cpf: str, token: str) -> bool:
        """Atualiza device_token via CPF"""
        cuidador = await self.get_by_cpf(cpf)
        if not cuidador:
            return False
        
        cuidador.device_token = token
        await self.db.commit()
        return True
    
    async def delete(self, id: int) -> bool:
        """Soft delete - marca como inativo"""
        cuidador = await self.get_by_id(id)
        if not cuidador:
            return False
        
        cuidador.ativo = False
        await self.db.commit()
        return True
