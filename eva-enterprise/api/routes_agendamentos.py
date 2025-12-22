from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from database.repositories.agendamento_repo import AgendamentoRepository
from database.repositories.historico_repo import HistoricoRepository
from schemas import (
    AgendamentoResponse, AgendamentoCreate, AgendamentoUpdate,
    HistoricoResponse, MakeCallRequest
)
from typing import List
from .calls import make_call_service # Assuming this exists or will be adapted

router = APIRouter()

# --- Agendamentos ---

@router.get("/agendamentos", response_model=List[AgendamentoResponse])
def list_agendamentos(idoso_id: int = None, db: Session = Depends(get_db)):
    repo = AgendamentoRepository(db)
    return repo.get_all(idoso_id=idoso_id)

@router.get("/agendamentos/{id}", response_model=AgendamentoResponse)
def get_agendamento(id: int, db: Session = Depends(get_db)):
    repo = AgendamentoRepository(db)
    agendamento = repo.get_by_id(id)
    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento not found")
    return agendamento

@router.post("/agendamentos", response_model=AgendamentoResponse)
def create_agendamento(agendamento: AgendamentoCreate, db: Session = Depends(get_db)):
    repo = AgendamentoRepository(db)
    return repo.create(agendamento.model_dump())

@router.put("/agendamentos/{id}", response_model=AgendamentoResponse)
def update_agendamento(id: int, agendamento: AgendamentoUpdate, db: Session = Depends(get_db)):
    repo = AgendamentoRepository(db)
    updated = repo.update(id, agendamento.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Agendamento not found")
    return updated

@router.delete("/agendamentos/{id}")
def delete_agendamento(id: int, db: Session = Depends(get_db)):
    repo = AgendamentoRepository(db)
    success = repo.delete(id)
    if not success:
        raise HTTPException(status_code=404, detail="Agendamento not found")
    return {"message": "Agendamento cancelled"}

# --- Historico & Calls ---

@router.get("/historico", response_model=List[HistoricoResponse])
def list_historico(idoso_id: int = None, db: Session = Depends(get_db)):
    repo = HistoricoRepository(db)
    return repo.list_all(idoso_id=idoso_id)

@router.post("/make-call")
async def trigger_call(request: MakeCallRequest):
    # Use existing logic from calls.py if possible or reimplement
    result = await make_call_service(request.telephone)
    return result

@router.post("/historico/atualizar-status")
async def update_call_status(agendamento_id: int, status: str, db: Session = Depends(get_db)):
    repo = AgendamentoRepository(db)
    repo.update_status(agendamento_id, status)
    return {"message": "Status updated"}
