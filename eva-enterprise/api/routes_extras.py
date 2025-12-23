from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db
from database.repositories.idoso_repo import IdosoRepository
from database.repositories.medicamento_repo import SinaisVitaisRepository, MedicamentoRepository
from database.repositories.alerta_repo import AlertaRepository
from typing import Dict, Any

router = APIRouter()

# --- Auth (Mock) ---

@router.post("/login")
async def login(credentials: Dict[str, str]):
    # Mock login
    if credentials.get("username") == "admin" and credentials.get("password") == "admin":
        return {"access_token": "mock_token", "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@router.post("/refresh-token")
async def refresh_token():
    return {"access_token": "new_mock_token", "token_type": "bearer"}

# --- Relatorios ---

@router.get("/relatorios/idoso/{id}")
async def get_idoso_report(id: int, db: AsyncSession = Depends(get_db)):
    idoso_repo = IdosoRepository(db)
    sinais_repo = SinaisVitaisRepository(db)
    alerta_repo = AlertaRepository(db)
    med_repo = MedicamentoRepository(db)

    idoso = await idoso_repo.get_by_id(id)
    if not idoso:
        raise HTTPException(status_code=404, detail="Idoso not found")

    sinais = await sinais_repo.get_weekly_report(id)
    insights = await alerta_repo.get_insights(id)
    meds = await med_repo.get_by_idoso(id)

    return {
        "idoso": {
            "nome": idoso.nome,
            "idade": "N/A" # Calculate from birthdate if available
        },
        "sinais_recentes": sinais,
        "insights": insights,
        "medicamentos_ativos": len(meds)
    }

# --- Gemini Session Placeholder ---
@router.post("/gemini/session")
async def create_session_instruction():
    return {"message": "Use WebSocket endpoint /media-stream for live session"}
