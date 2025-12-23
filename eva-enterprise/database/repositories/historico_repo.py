from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Optional, List
import datetime


class HistoricoRepository:
    """Repository para gerenciar histórico de eventos e alertas"""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def criar_alerta(self, tipo: str, descricao: str):
        """
        Cria um novo alerta no sistema
        
        Args:
            tipo: Tipo do alerta (ex: 'medicamento', 'emergencia', 'lembrete')
            descricao: Descrição detalhada do alerta
            
        Returns:
            Objeto Alerta criado
        """
        from ..models import Alerta
        
        novo_alerta = Alerta(
            tipo=tipo,
            descricao=descricao,
            criado_em=datetime.datetime.now()
        )
        self.db.add(novo_alerta)
        await self.db.commit()
        await self.db.refresh(novo_alerta)
        return novo_alerta

    async def create(self, dados: dict) -> int:
        """
        Cria um novo registro no histórico
        
        Args:
            dados: Dicionário com os dados do histórico
                - agendamento_id: ID do agendamento relacionado
                - idoso_id: ID do idoso
                - evento: Descrição do evento
                - status: Status do evento
                - observacoes: Observações adicionais (opcional)
                
        Returns:
            ID do histórico criado
        """
        from ..models import Historico
        
        historico = Historico(
            agendamento_id=dados.get('agendamento_id'),
            idoso_id=dados.get('idoso_id'),
            evento=dados.get('evento'),
            status=dados.get('status'),
            observacoes=dados.get('observacoes'),
            criado_em=datetime.datetime.now()
        )
        self.db.add(historico)
        await self.db.commit()
        await self.db.refresh(historico)
        return historico.id

    async def update(self, id: int, dados: dict) -> Optional[object]:
        """
        Atualiza registro existente no histórico
        
        Args:
            id: ID do histórico a ser atualizado
            dados: Dicionário com os campos a serem atualizados
            
        Returns:
            Objeto Historico atualizado ou None se não encontrado
        """
        from ..models import Historico
        
        query = select(Historico).filter(Historico.id == id)
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

    async def get_by_id(self, id: int) -> Optional[object]:
        """
        Busca histórico por ID
        
        Args:
            id: ID do histórico
            
        Returns:
            Objeto Historico ou None se não encontrado
        """
        from ..models import Historico
        query = select(Historico).filter(Historico.id == id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        idoso_id: Optional[int] = None,
        agendamento_id: Optional[int] = None
    ) -> List[object]:
        """
        Lista histórico com filtros e paginação
        
        Args:
            skip: Número de registros a pular (paginação)
            limit: Número máximo de registros a retornar
            idoso_id: Filtrar por ID do idoso (opcional)
            agendamento_id: Filtrar por ID do agendamento (opcional)
            
        Returns:
            Lista de objetos Historico
        """
        from ..models import Historico, Idoso
        
        query = select(Historico).join(Idoso)
        
        if idoso_id:
            query = query.filter(Historico.idoso_id == idoso_id)
        
        if agendamento_id:
            query = query.filter(Historico.agendamento_id == agendamento_id)
            
        result = await self.db.execute(query.order_by(
            Historico.criado_em.desc()
        ).offset(skip).limit(limit))
        return result.scalars().all()

    async def list_by_periodo(
        self,
        data_inicio: datetime.datetime,
        data_fim: datetime.datetime,
        idoso_id: Optional[int] = None
    ) -> List[object]:
        """
        Lista histórico por período
        
        Args:
            data_inicio: Data inicial do período
            data_fim: Data final do período
            idoso_id: Filtrar por ID do idoso (opcional)
            
        Returns:
            Lista de objetos Historico no período especificado
        """
        from ..models import Historico
        
        query = select(Historico).filter(
            Historico.criado_em >= data_inicio,
            Historico.criado_em <= data_fim
        )
        
        if idoso_id:
            query = query.filter(Historico.idoso_id == idoso_id)
        
        result = await self.db.execute(query.order_by(Historico.criado_em.desc()))
        return result.scalars().all()

    async def delete(self, id: int) -> bool:
        """
        Remove um histórico
        
        Args:
            id: ID do histórico a ser removido
            
        Returns:
            True se removido com sucesso, False caso contrário
        """
        from ..models import Historico
        
        query = select(Historico).filter(Historico.id == id)
        result = await self.db.execute(query)
        historico = result.scalar_one_or_none()
        if historico:
            await self.db.delete(historico)
            await self.db.commit()
            return True
        return False