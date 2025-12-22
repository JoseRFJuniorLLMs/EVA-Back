from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from database.repositories.medicamento_repo import MedicamentoRepository, SinaisVitaisRepository
from schemas import (
    MedicamentoResponse, MedicamentoCreate, MedicamentoUpdate,
    SinaisVitaisResponse, SinaisVitaisCreate
)
from typing import List

router = APIRouter()

# --- Medicamentos ---

@router.get("/", response_model=List[MedicamentoResponse])
async def list_medicamentos(idoso_id: int = None, db: Session = Depends(get_db)):
    repo = MedicamentoRepository(db)
    if idoso_id:
        return await repo.get_by_idoso(idoso_id)
    return [] 

@router.get("/{id}", response_model=MedicamentoResponse)
async def get_medicamento(id: int, db: Session = Depends(get_db)):
    repo = MedicamentoRepository(db)
    med = repo.get_by_id(id)
    if not med:
        raise HTTPException(status_code=404, detail="Medicamento not found")
    return med

@router.post("/", response_model=MedicamentoResponse)
def create_medicamento(med: MedicamentoCreate, db: Session = Depends(get_db)):
    repo = MedicamentoRepository(db)
    return repo.create(med.model_dump())

@router.put("/{id}", response_model=MedicamentoResponse)
def update_medicamento(id: int, med: MedicamentoUpdate, db: Session = Depends(get_db)):
    repo = MedicamentoRepository(db)
    updated = repo.update(id, med.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Medicamento not found")
    return updated

@router.delete("/{id}")
def delete_medicamento(id: int, db: Session = Depends(get_db)):
    repo = MedicamentoRepository(db)
    success = repo.delete(id)
    if not success:
        raise HTTPException(status_code=404, detail="Medicamento not found")
    return {"message": "Medicamento disabled"}

@router.post("/confirmar")
def confirm_medicamento(id: int, agendamento_id: int, db: Session = Depends(get_db)):
    repo = MedicamentoRepository(db)
    repo.confirm_intake(id, agendamento_id)
    return {"message": "Confirmed"}

# --- Sinais Vitais ---

@router.get("/sinais-vitais/{idoso_id}", response_model=List[SinaisVitaisResponse])
def list_sinais_vitais(idoso_id: int, db: Session = Depends(get_db)):
    repo = SinaisVitaisRepository(db)
    return repo.get_by_idoso(idoso_id)

@router.post("/sinais-vitais", response_model=SinaisVitaisResponse)
def create_sinal_vital(sinal: SinaisVitaisCreate, db: Session = Depends(get_db)):
    repo = SinaisVitaisRepository(db)
    return repo.create(sinal.model_dump())

@router.get("/sinais-vitais/relatorio/{idoso_id}", response_model=List[SinaisVitaisResponse])
def get_relatorio_sinais(idoso_id: int, db: Session = Depends(get_db)):
    repo = SinaisVitaisRepository(db)
    return repo.get_weekly_report(idoso_id)
