from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter()

# --- Placeholders para evitar 404 no Frontend ---

@router.get("/metricas/", tags=["Placeholders"])
async def get_metricas():
    return {"total_idosos": 0, "alertas_ativos": 0}

@router.get("/contatos-alerta/", tags=["Placeholders"])
async def get_contatos_alerta():
    return []

@router.get("/timeline/", tags=["Placeholders"])
async def get_timeline():
    return []

@router.get("/formas-pagamento/", tags=["Placeholders"])
async def get_formas_pagamento():
    return []

@router.get("/biografias/", tags=["Placeholders"])
async def get_biografias():
    return []

@router.get("/finops/", tags=["Placeholders"])
async def get_finops():
    return {"receita": 0, "despesas": 0}

@router.get("/fluxos-alerta/", tags=["Placeholders"])
async def get_fluxos_alerta():
    return []

@router.get("/genealogia/", tags=["Placeholders"])
async def get_genealogia():
    return []

@router.get("/legacy-assets/", tags=["Placeholders"])
async def get_legacy_assets():
    return []

@router.get("/emotional-analytics/", tags=["Placeholders"])
async def get_emotional_analytics():
    return {"humor_medio": "neutro"}
