"""
API de Agendamentos - Endpoints para gerenciar agendamentos
"""
from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from database.connection import get_db
from database.repositories.agendamento_repo import AgendamentoRepository

router = APIRouter()

# ==================== SCHEMAS ====================

class AgendamentoCreate(BaseModel):
    """Schema para criar agendamento"""
    idoso_id: int
    tipo: str
    descricao: str
    horario: datetime
    telefone: Optional[str] = None
    recorrente: bool = False
    frequencia: Optional[str] = None


class AgendamentoUpdate(BaseModel):
    """Schema para atualizar agendamento"""
    tipo: Optional[str] = None
    descricao: Optional[str] = None
    horario: Optional[datetime] = None
    telefone: Optional[str] = None
    status: Optional[str] = None
    recorrente: Optional[bool] = None
    frequencia: Optional[str] = None


class AgendamentoResponse(BaseModel):
    """Schema de resposta de agendamento"""
    id: int
    idoso_id: int
    idoso_nome: Optional[str] = None
    tipo: Optional[str] = None
    descricao: Optional[str] = None
    horario: datetime
    status: str
    telefone: Optional[str] = None
    tentativas_realizadas: int = 0
    recorrente: bool = False
    frequencia: Optional[str] = None
    criado_em: Optional[datetime] = None
    
    class Config:
        from_attributes = True


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
    limit: int = 100,
    idoso_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Lista agendamentos com filtros opcionais"""
    repo = AgendamentoRepository(db)
    return await repo.get_all(skip=skip, limit=limit, idoso_id=idoso_id)


@router.put("/{agendamento_id}", response_model=AgendamentoResponse)
async def atualizar_agendamento(
    agendamento_id: int,
    dados: AgendamentoUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Atualiza dados de um agendamento"""
    repo = AgendamentoRepository(db)
    
    update_data = {k: v for k, v in dados.model_dump().items() if v is not None}
    
    agendamento = await repo.update(agendamento_id, update_data)
    
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
    
    status_validos = ['pendente', 'em_andamento', 'concluido', 'cancelado', 'falhou', 'retry_agendado']
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
