from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from database.connection import get_db
from database.repositories.alerta_repo import AlertaRepository
from schemas import (
    AlertaResponse, AlertaCreate,
    PsicologiaInsightResponse, TopicoAfetivoResponse, InsightGenerate
)

from utils.pagination import get_pagination_params, PaginationParams, PaginatedResponse
from typing import List, Optional

router = APIRouter()

# --- Alertas ---

@router.get("/", response_model=List[AlertaResponse])
async def list_alertas(tipo: str = None, limit: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """Lista alertas recentes. Regra: se tipo for passado, retorna 1. Se não, retorna 10 por padrão."""
    if limit is None:
        limit = 1 if tipo else 10
    repo = AlertaRepository(db)
    return await repo.get_recent_alerts(limit=limit, tipo=tipo)

@router.post("/", response_model=AlertaResponse)
async def create_alerta(alerta: AlertaCreate, db: AsyncSession = Depends(get_db)):
    repo = AlertaRepository(db)
    return await repo.create_alerta(
        idoso_id=alerta.idoso_id,
        tipo=alerta.tipo,
        severidade=alerta.severidade,
        mensagem=alerta.mensagem,
        destinatarios=alerta.destinatarios
    )

@router.get("/{id}", response_model=AlertaResponse)
async def get_alerta(id: int, db: AsyncSession = Depends(get_db)):
    repo = AlertaRepository(db)
    alerta = await repo.get_by_id(id)
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta not found")
    return alerta

@router.post("/{id}/resolver")
async def resolve_alerta(id: int, nota: str = None, db: AsyncSession = Depends(get_db)):
    repo = AlertaRepository(db)
    updated = await repo.resolve_alerta(id, nota)
    if not updated:
        raise HTTPException(status_code=404, detail="Alerta not found")
    return {"message": "Alerta resolved"}

# --- Insights & Psicologia ---

@router.get("/psicologia-insights/{idoso_id}")
async def get_insights(
    idoso_id: int,
    pagination: PaginationParams = Depends(get_pagination_params),
    db: AsyncSession = Depends(get_db)
):
    """Lista insights psicológicos (paginado)"""
    repo = AlertaRepository(db)
    results = await repo.get_insights(idoso_id)
    
    # Paginação manual
    total = len(results)
    start = pagination.offset
    end = start + pagination.limit
    items = results[start:end]
    
    return PaginatedResponse[PsicologiaInsightResponse].create(
        items=items,
        total=total,
        page=pagination.page,
        limit=pagination.limit
    )[:1]

@router.post("/psicologia-insights/", response_model=PsicologiaInsightResponse)
async def generate_insight(data: InsightGenerate, db: AsyncSession = Depends(get_db)):
    repo = AlertaRepository(db)
    # Mock Logic -> In real app, call LLM here
    mensagem = f"Insight gerado por IA para o idoso {data.idoso_id}."
    return await repo.create_insight(data.idoso_id, mensagem, tipo='positivo', relevancia='alta')

@router.get("/topicos-afetivos/{idoso_id}", response_model=List[TopicoAfetivoResponse])
async def get_topicos(idoso_id: int, db: AsyncSession = Depends(get_db)):
    repo = AlertaRepository(db)
    results = await repo.get_topicos(idoso_id)
    return results[:1]

@router.post("/topicos-afetivos/atualizar")
async def update_topico(idoso_id: int, topico: str, sentimento: str = None, db: AsyncSession = Depends(get_db)):
    repo = AlertaRepository(db)
    updated = await repo.update_topico(idoso_id, topico, sentimento)
    return {"message": "Topic updated", "topico": updated.topico}

@router.get("/psicologia-insights/historico/{idoso_id}/")
async def get_emotional_history(idoso_id: int):
    # Returns mock time-series data for Recharts
    return [
        {"data": "Seg", "feliz": 65, "neutro": 20, "triste": 15},
        {"data": "Ter", "feliz": 55, "neutro": 30, "triste": 15},
        {"data": "Qua", "feliz": 40, "neutro": 20, "triste": 40},
        {"data": "Qui", "feliz": 70, "neutro": 20, "triste": 10},
        {"data": "Sex", "feliz": 80, "neutro": 15, "triste": 5},
        {"data": "Sáb", "feliz": 90, "neutro": 5, "triste": 5},
        {"data": "Dom", "feliz": 85, "neutro": 10, "triste": 5},
    ]

# ==================== HEALTH THINKING AUDIT ====================

@router.get("/health/thinking-process/{alerta_id}", tags=["Alertas"])
async def get_thinking_process(
    alerta_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Retorna o processo de pensamento da IA para um alerta específico"""
    query = text("""
        SELECT * FROM health_thinking_audit 
        WHERE id = (SELECT ligacao_id FROM alertas WHERE id = :id)
    """)
    result = await db.execute(query, {"id": alerta_id})
    row = result.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Thinking process not found for this alert")
        
    return dict(row._mapping)
@router.patch("/health/thinking-process/{id}/mark-notified", tags=["Alertas"])
async def mark_thinking_notified(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    """Marca que o cuidador foi notificado sobre um insight de pensamento"""
    query = text("""
        UPDATE health_thinking_audit 
        SET caregiver_notified = True, notified_at = NOW() 
        WHERE id = :id
    """)
    await db.execute(query, {"id": id})
    await db.commit()
    return {"message": "Marked as notified"}
