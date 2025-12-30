from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel
from fastapi import Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T')

class PaginationParams(BaseModel):
    """Parâmetros de paginação"""
    page: int = 1
    limit: int = 10
    
    @property
    def offset(self) -> int:
        """Calcula offset baseado em page e limit"""
        return (self.page - 1) * self.limit
    
    class Config:
        frozen = True

class PaginationMeta(BaseModel):
    """Metadados de paginação"""
    page: int
    limit: int
    total: int
    pages: int
    has_next: bool
    has_prev: bool

class PaginatedResponse(BaseModel, Generic[T]):
    """Resposta paginada genérica"""
    items: List[T]
    pagination: PaginationMeta
    
    @classmethod
    def create(
        cls, 
        items: List[T], 
        total: int, 
        page: int, 
        limit: int
    ) -> "PaginatedResponse[T]":
        """Cria resposta paginada com metadados calculados"""
        pages = (total + limit - 1) // limit if limit > 0 else 0
        
        return cls(
            items=items,
            pagination=PaginationMeta(
                page=page,
                limit=limit,
                total=total,
                pages=pages,
                has_next=page < pages,
                has_prev=page > 1
            )
        )

def get_pagination_params(
    page: int = Query(1, ge=1, description="Número da página (inicia em 1)"),
    limit: int = Query(10, ge=1, le=100, description="Itens por página (máximo 100)")
) -> PaginationParams:
    """Dependency para extrair parâmetros de paginação"""
    return PaginationParams(page=page, limit=limit)

async def paginate_query(
    db: AsyncSession,
    query,
    page: int = 1,
    limit: int = 10
) -> tuple[List, int]:
    """
    Aplica paginação a uma query SQLAlchemy.
    
    Args:
        db: Sessão do banco
        query: Query SQLAlchemy
        page: Número da página
        limit: Itens por página
    
    Returns:
        Tupla (items, total_count)
    """
    # Contar total de registros
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0
    
    # Aplicar paginação
    offset = (page - 1) * limit
    paginated_query = query.offset(offset).limit(limit)
    
    # Executar query
    result = await db.execute(paginated_query)
    items = result.scalars().all()
    
    return items, total
