from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db
from database.repositories.medicamento_repo import MedicamentoRepository, SinaisVitaisRepository
from schemas import (
    MedicamentoCreate, MedicamentoResponse,
    SinaisVitaisCreate, SinaisVitaisResponse,
    MessageResponse
)
from typing import List

router = APIRouter()

# --- Medicamentos ---

@router.get("/{idoso_id}", response_model=List[MedicamentoResponse])
async def list_medicamentos(idoso_id: int, db: AsyncSession = Depends(get_db)):
    """Lista medicamentos. Regra: como passa idoso_id, limita a 1 item."""
    repo = MedicamentoRepository(db)
    results = await repo.get_by_idoso(idoso_id)
    return results[:1]


@router.post("/", response_model=MedicamentoResponse)
async def create_medicamento(medicamento: MedicamentoCreate, db: AsyncSession = Depends(get_db)):
    repo = MedicamentoRepository(db)
    return await repo.create(medicamento.model_dump())


@router.delete("/{id}", response_model=MessageResponse)
async def delete_medicamento(id: int, db: AsyncSession = Depends(get_db)):
    repo = MedicamentoRepository(db)
    success = await repo.delete(id)
    if not success:
        raise HTTPException(status_code=404, detail="Medicamento not found")
    return {"message": "Medicamento disabled"}

@router.post("/confirmar", response_model=MessageResponse)
async def confirm_medicamento(id: int, agendamento_id: int, db: AsyncSession = Depends(get_db)):
    repo = MedicamentoRepository(db)
    await repo.confirm_intake(id, agendamento_id)
    return {"message": "Confirmed"}

# --- Sinais Vitais ---

@router.get("/sinais-vitais/{idoso_id}", response_model=List[SinaisVitaisResponse])
async def list_sinais_vitais(idoso_id: int, db: AsyncSession = Depends(get_db)):
    """Lista sinais vitais. Regra: como passa idoso_id, limita a 1 item."""
    repo = SinaisVitaisRepository(db)
    results = await repo.get_by_idoso(idoso_id)
    return results[:1]

@router.post("/sinais-vitais", response_model=SinaisVitaisResponse)
async def create_sinal_vital(sinal: SinaisVitaisCreate, db: AsyncSession = Depends(get_db)):
    repo = SinaisVitaisRepository(db)
    return await repo.create(sinal.model_dump())

@router.get("/sinais-vitais/relatorio/{idoso_id}", response_model=List[SinaisVitaisResponse])
async def get_relatorio_sinais(idoso_id: int, db: AsyncSession = Depends(get_db)):
    repo = SinaisVitaisRepository(db)
    return await repo.get_weekly_report(idoso_id)
