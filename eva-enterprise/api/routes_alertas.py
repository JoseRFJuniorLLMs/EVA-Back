from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db
from database.repositories.alerta_repo import AlertaRepository
from schemas import (
    AlertaResponse, AlertaCreate,
    PsicologiaInsightResponse, TopicoAfetivoResponse, InsightGenerate
)
from typing import List

router = APIRouter()

# --- Alertas ---

@router.get("/", response_model=List[AlertaResponse])
async def list_alertas(tipo: str = None, limit: int = 50, db: AsyncSession = Depends(get_db)):
    repo = AlertaRepository(db)
    return await repo.get_recent_alerts(limit=limit, tipo=tipo)

@router.post("/", response_model=AlertaResponse)
async def create_alerta(alerta: AlertaCreate, db: AsyncSession = Depends(get_db)):
    repo = AlertaRepository(db)
    return await repo.create_alerta(alerta.tipo, alerta.descricao)

@router.get("/{id}", response_model=AlertaResponse)
async def get_alerta(id: int, db: AsyncSession = Depends(get_db)):
    repo = AlertaRepository(db)
    alerta = await repo.get_by_id(id)
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta not found")
    return alerta

@router.post("/enviar-familiar")
async def send_alert_to_family(alerta_id: int):
    # Mock logic to send notification
    return {"message": "Notification sent to family"}

# --- Insights & Psicologia ---

@router.get("/psicologia-insights/{idoso_id}", response_model=List[PsicologiaInsightResponse])
async def get_insights(idoso_id: int, db: AsyncSession = Depends(get_db)):
    repo = AlertaRepository(db)
    return await repo.get_insights(idoso_id)

@router.post("/psicologia-insights/", response_model=PsicologiaInsightResponse)
async def generate_insight(data: InsightGenerate, db: AsyncSession = Depends(get_db)):
    repo = AlertaRepository(db)
    # Mock Logic -> In real app, call LLM here
    conteudo = f"Insight gerado por IA para o idoso {data.idoso_id}."
    return await repo.create_insight(data.idoso_id, conteudo, relevancia=8)

@router.get("/topicos-afetivos/{idoso_id}", response_model=List[TopicoAfetivoResponse])
async def get_topicos(idoso_id: int, db: AsyncSession = Depends(get_db)):
    repo = AlertaRepository(db)
    return await repo.get_topicos(idoso_id)

@router.post("/topicos-afetivos/atualizar")
async def update_topico(idoso_id: int, topico: str, db: AsyncSession = Depends(get_db)):
    repo = AlertaRepository(db)
    updated = await repo.update_topico(idoso_id, topico)
    return {"message": "Topic updated", "topico": updated.topico}

@router.get("/psicologia-insights/historico/{idoso_id}/")
async def get_emotional_history(idoso_id: int):
    # Returns mock time-series data matching the frontend Recharts structure
    # Frontend expects: [{data: 'Mon', feliz: 40, neutro: 20, triste: 10}, ...]
    
    return [
        {"data": "Seg", "feliz": 65, "neutro": 20, "triste": 15},
        {"data": "Ter", "feliz": 55, "neutro": 30, "triste": 15},
        {"data": "Qua", "feliz": 40, "neutro": 20, "triste": 40},
        {"data": "Qui", "feliz": 70, "neutro": 20, "triste": 10},
        {"data": "Sex", "feliz": 80, "neutro": 15, "triste": 5},
        {"data": "Sáb", "feliz": 90, "neutro": 5, "triste": 5},
        {"data": "Dom", "feliz": 85, "neutro": 10, "triste": 5},
    ]
