from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db
from database.repositories.medicamento_repo import MedicamentoRepository, SinaisVitaisRepository
from typing import List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# Schemas simples para Medicamentos (pode ser movido para schemas.py)
class MedicamentoBase(BaseModel):
    nome: str
    dosagem: str
    horarios: List[str]
    principio_ativo: str = None
    observacoes: str = None

class MedicamentoCreate(MedicamentoBase):
    idoso_id: int

class MedicamentoResponse(MedicamentoBase):
    id: int
    idoso_id: int
    ativo: bool

class SinaisVitaisCreate(BaseModel):
    idoso_id: int
    tipo: str
    valor: str
    unidade: str
    observacoes: str = None

class SinaisVitaisResponse(SinaisVitaisCreate):
    id: int
    data_medicao: datetime


# --- Medicamentos ---

@router.get("/{idoso_id}", response_model=List[dict])
async def list_medicamentos(idoso_id: int, db: AsyncSession = Depends(get_db)):
    repo = MedicamentoRepository(db)
    return await repo.get_by_idoso(idoso_id)


@router.post("/", response_model=dict)
async def create_medicamento(dados: dict, db: AsyncSession = Depends(get_db)):
    repo = MedicamentoRepository(db)
    return await repo.create(dados)


@router.delete("/{id}")
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
