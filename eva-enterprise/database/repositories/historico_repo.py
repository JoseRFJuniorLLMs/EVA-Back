from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from ..models import HistoricoLigacao, Idoso
from typing import Optional, List
import datetime

class HistoricoRepository:
    """Repository para gerenciar histórico de ligações"""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, dados: dict) -> int:
        """
        Cria um novo registro no histórico de ligações
        """
        historico = HistoricoLigacao(**dados)
        self.db.add(historico)
        await self.db.commit()
        await self.db.refresh(historico)
        return historico.id

    async def update(self, id: int, dados: dict) -> Optional[HistoricoLigacao]:
        """
        Atualiza registro existente no histórico
        """
        query = select(HistoricoLigacao).filter(HistoricoLigacao.id == id)
        result = await self.db.execute(query)
        historico = result.scalar_one_or_none()
        if historico:
            for key, value in dados.items():
                if hasattr(historico, key):
                    setattr(historico, key, value)
            await self.db.commit()
            await self.db.refresh(historico)
            return historico
        return None

    async def get_by_id(self, id: int) -> Optional[HistoricoLigacao]:
        query = select(HistoricoLigacao).filter(HistoricoLigacao.id == id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        idoso_id: Optional[int] = None,
        agendamento_id: Optional[int] = None
    ) -> List[HistoricoLigacao]:
        query = select(HistoricoLigacao).join(Idoso)
        
        if idoso_id:
            query = query.filter(HistoricoLigacao.idoso_id == idoso_id)
        
        if agendamento_id:
            query = query.filter(HistoricoLigacao.agendamento_id == agendamento_id)
            
        result = await self.db.execute(query.order_by(
            HistoricoLigacao.criado_em.desc()
        ).offset(skip).limit(limit))
        return result.scalars().all()

    async def list_by_periodo(
        self,
        data_inicio: datetime.datetime,
        data_fim: datetime.datetime,
        idoso_id: Optional[int] = None
    ) -> List[HistoricoLigacao]:
        query = select(HistoricoLigacao).filter(
            HistoricoLigacao.inicio_chamada >= data_inicio,
            HistoricoLigacao.inicio_chamada <= data_fim
        )
        
        if idoso_id:
            query = query.filter(HistoricoLigacao.idoso_id == idoso_id)
        
        result = await self.db.execute(query.order_by(HistoricoLigacao.inicio_chamada.desc()))
        return result.scalars().all()

    async def delete(self, id: int) -> bool:
        query = select(HistoricoLigacao).filter(HistoricoLigacao.id == id)
        result = await self.db.execute(query)
        historico = result.scalar_one_or_none()
        if historico:
            await self.db.delete(historico)
            await self.db.commit()
            return True
        return False