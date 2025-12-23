from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from database.connection import get_db
from database.repositories.agendamento_repo import AgendamentoRepository
from schemas import AgendamentoCreate, AgendamentoResponse

router = APIRouter()

# ==================== ENDPOINTS ====================

@router.post("/", response_model=AgendamentoResponse, status_code=201)
async def criar_agendamento(
    agendamento: AgendamentoCreate,
    db: AsyncSession = Depends(get_db)
):
    """Cria um novo agendamento"""
    repo = AgendamentoRepository(db)
    
    try:
        novo = await repo.create(agendamento.model_dump())
        return novo
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao criar agendamento: {str(e)}")


@router.get("/{agendamento_id}", response_model=AgendamentoResponse)
async def obter_agendamento(
    agendamento_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Busca agendamento por ID com dados do idoso"""
    repo = AgendamentoRepository(db)
    agendamento = await repo.get_by_id(agendamento_id)
    
    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    
    return agendamento


@router.get("/", response_model=List[AgendamentoResponse])
async def listar_agendamentos(
    skip: int = 0,
    limit: Optional[int] = None,
    idoso_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Lista agendamentos com filtros opcionais. 
    Regra: se idoso_id for passado, retorna 1. Se não, retorna 10 por padrão."""
    if limit is None:
        limit = 1 if idoso_id else 10
        
    repo = AgendamentoRepository(db)
    return await repo.get_all(skip=skip, limit=limit, idoso_id=idoso_id)


@router.put("/{agendamento_id}", response_model=AgendamentoResponse)
async def atualizar_agendamento(
    agendamento_id: int,
    dados: dict = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """Atualiza dados de um agendamento"""
    repo = AgendamentoRepository(db)
    
    agendamento = await repo.update(agendamento_id, dados)
    
    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    
    return agendamento


@router.patch("/{agendamento_id}/status")
async def atualizar_status(
    agendamento_id: int,
    status: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db)
):
    """Atualiza apenas o status de um agendamento"""
    repo = AgendamentoRepository(db)
    
    status_validos = ['agendado', 'em_andamento', 'concluido', 'cancelado', 'falhou', 'retry_agendado']
    if status not in status_validos:
        raise HTTPException(
            status_code=400,
            detail=f"Status inválido. Valores aceitos: {', '.join(status_validos)}"
        )
    
    agendamento = await repo.update_status(agendamento_id, status)
    
    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    
    return {
        "message": "Status atualizado com sucesso",
        "agendamento_id": agendamento_id,
        "novo_status": status
    }
