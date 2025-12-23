from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db
from database.repositories.historico_repo import HistoricoRepository
from schemas import HistoricoResponse
from typing import List, Optional

router = APIRouter()

@router.get("/", response_model=List[HistoricoResponse])
async def list_historico(
    idoso_id: Optional[int] = None,
    agendamento_id: Optional[int] = None,
    skip: int = 0,
    limit: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Lista histórico de ligações.
    Regra: se idoso_id ou agendamento_id for passado, limita a 1. Se não, 10 por padrão."""
    if limit is None:
        limit = 1 if (idoso_id or agendamento_id) else 10
        
    repo = HistoricoRepository(db)
    historico = await repo.list_all(skip=skip, limit=limit, idoso_id=idoso_id, agendamento_id=agendamento_id)
    return [HistoricoResponse.model_validate(h) for h in historico]

@router.get("/{id}", response_model=HistoricoResponse)
async def get_detalhes_ligacao(id: int, db: AsyncSession = Depends(get_db)):
    """Obtém detalhes completos de uma ligação do histórico"""
    repo = HistoricoRepository(db)
    historico = await repo.get_by_id(id)
    if not historico:
        raise HTTPException(status_code=404, detail="Registro de histórico não encontrado")
    return HistoricoResponse.model_validate(historico)
