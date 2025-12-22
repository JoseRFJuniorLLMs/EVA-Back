from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from database.connection import get_db
from database.repositories.agendamento_repo import AgendamentoRepository
from database.repositories.historico_repo import HistoricoRepository
from schemas import (
    AgendamentoResponse, AgendamentoCreate, AgendamentoUpdate,
    HistoricoResponse
)
from typing import List
from pydantic import BaseModel

router = APIRouter()


# --- Pydantic model para atualizar status ---
class UpdateStatusRequest(BaseModel):
    agendamento_id: int
    status: str


# ===============================
# AGENDAMENTOS
# ===============================

@router.get("/", response_model=List[AgendamentoResponse])
async def list_agendamentos(idoso_id: int = None, db: AsyncSession = Depends(get_db)):
    repo = AgendamentoRepository(db)
    try:
        agendamentos = await repo.get_all(idoso_id=idoso_id)
        return agendamentos or []
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar agendamentos: {str(e)}")


@router.get("/{id}", response_model=AgendamentoResponse)
async def get_agendamento(id: int, db: AsyncSession = Depends(get_db)):
    repo = AgendamentoRepository(db)
    try:
        agendamento = await repo.get_by_id(id)
        if not agendamento:
            raise HTTPException(status_code=404, detail="Agendamento não encontrado")
        return agendamento
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar agendamento: {str(e)}")


@router.post("/", response_model=AgendamentoResponse)
async def create_agendamento(agendamento: AgendamentoCreate, db: AsyncSession = Depends(get_db)):
    repo = AgendamentoRepository(db)
    try:
        new_agendamento = await repo.create(agendamento.model_dump())
        return new_agendamento
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar agendamento: {str(e)}")


@router.put("/{id}", response_model=AgendamentoResponse)
async def update_agendamento(id: int, agendamento: AgendamentoUpdate, db: AsyncSession = Depends(get_db)):
    repo = AgendamentoRepository(db)
    try:
        updated = await repo.update(id, agendamento.model_dump(exclude_unset=True))
        if not updated:
            raise HTTPException(status_code=404, detail="Agendamento não encontrado")
        return updated
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar agendamento: {str(e)}")


@router.delete("/{id}")
async def delete_agendamento(id: int, db: AsyncSession = Depends(get_db)):
    repo = AgendamentoRepository(db)
    try:
        success = await repo.delete(id)
        if not success:
            raise HTTPException(status_code=404, detail="Agendamento não encontrado")
        return {"message": "Agendamento cancelado"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar agendamento: {str(e)}")


# ===============================
# HISTÓRICO
# ===============================

@router.get("/historico/", response_model=List[HistoricoResponse])
async def list_historico(idoso_id: int = None, db: AsyncSession = Depends(get_db)):
    repo = HistoricoRepository(db)
    try:
        historico = await repo.list_all(idoso_id=idoso_id)
        return historico or []
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar histórico: {str(e)}")


@router.post("/historico/atualizar-status")
async def update_call_status(req: UpdateStatusRequest, db: AsyncSession = Depends(get_db)):
    repo = AgendamentoRepository(db)
    try:
        updated = await repo.update_status(req.agendamento_id, req.status)
        if not updated:
            raise HTTPException(status_code=404, detail="Agendamento não encontrado para atualizar status")
        return {"message": "Status atualizado"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar status: {str(e)}")
