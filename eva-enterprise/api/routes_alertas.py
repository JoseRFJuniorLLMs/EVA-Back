from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
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
def list_alertas(tipo: str = None, limit: int = 50, db: Session = Depends(get_db)):
    repo = AlertaRepository(db)
    return repo.get_recent_alerts(limit=limit, tipo=tipo)

@router.post("/", response_model=AlertaResponse)
def create_alerta(alerta: AlertaCreate, db: Session = Depends(get_db)):
    repo = AlertaRepository(db)
    return repo.create_alerta(alerta.tipo, alerta.descricao)

@router.get("/{id}", response_model=AlertaResponse)
def get_alerta(id: int, db: Session = Depends(get_db)):
    repo = AlertaRepository(db)
    alerta = repo.get_by_id(id)
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta not found")
    return alerta

@router.post("/enviar-familiar")
def send_alert_to_family(alerta_id: int):
    # Mock logic to send notification
    return {"message": "Notification sent to family"}

# --- Insights & Psicologia ---

@router.get("/psicologia-insights/{idoso_id}", response_model=List[PsicologiaInsightResponse])
def get_insights(idoso_id: int, db: Session = Depends(get_db)):
    repo = AlertaRepository(db)
    return repo.get_insights(idoso_id)

@router.post("/psicologia-insights", response_model=PsicologiaInsightResponse)
def generate_insight(data: InsightGenerate, db: Session = Depends(get_db)):
    repo = AlertaRepository(db)
    # Mock Logic -> In real app, call LLM here
    conteudo = f"Insight gerado por IA para o idoso {data.idoso_id}."
    return repo.create_insight(data.idoso_id, conteudo, relevancia=8)

@router.get("/topicos-afetivos/{idoso_id}", response_model=List[TopicoAfetivoResponse])
def get_topicos(idoso_id: int, db: Session = Depends(get_db)):
    repo = AlertaRepository(db)
    return repo.get_topicos(idoso_id)

@router.post("/topicos-afetivos/atualizar")
def update_topico(idoso_id: int, topico: str, db: Session = Depends(get_db)):
    repo = AlertaRepository(db)
    updated = repo.update_topico(idoso_id, topico)
    return {"message": "Topic updated", "topico": updated.topico}

@router.get("/psicologia-insights/historico/{idoso_id}")
def get_emotional_history(idoso_id: int):
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
