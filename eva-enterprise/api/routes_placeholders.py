from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from database.connection import get_db
from database.models import Biografia, Idoso, Alerta, AssinaturaEntidade, LegadoDigital
from typing import List, Dict, Any

router = APIRouter()

# --- Placeholders para evitar 404 no Frontend ---

@router.get("/metricas/", tags=["Placeholders"])
async def get_metricas(db: AsyncSession = Depends(get_db)):
    total_idosos = await db.scalar(select(func.count(Idoso.id)))
    alertas_ativos = await db.scalar(select(func.count(Alerta.id)).where(Alerta.resolvido == False))
    return {"total_idosos": total_idosos or 0, "alertas_ativos": alertas_ativos or 0}

@router.get("/contatos-alerta/", tags=["Placeholders"])
async def get_contatos_alerta():
    return []


@router.get("/formas-pagamento/", tags=["Placeholders"])
async def get_formas_pagamento():
    return [
        {"id": "credit_card", "nome": "Cartão de Crédito"},
        {"id": "pix", "nome": "PIX"},
        {"id": "wise", "nome": "Wise Transfer"}
    ]

@router.get("/biografias/", tags=["Placeholders"])
async def get_biografias(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Biografia))
    return result.scalars().all()

@router.get("/finops/", tags=["Placeholders"])
async def get_finops(db: AsyncSession = Depends(get_db)):
    # Simulado por enquanto, mas poderia vir de assinaturas
    return {"receita": 15000.0, "despesas": 4500.0}

@router.get("/fluxos-alerta/", tags=["Placeholders"])
async def get_fluxos_alerta():
    return []

@router.get("/genealogia/", tags=["Placeholders"])
async def get_genealogia():
    # Isso geralmente depende de idoso_id, mas a rota original não tem
    return []

@router.get("/legacy-assets/", tags=["Placeholders"])
async def get_legacy_assets(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LegadoDigital))
    return result.scalars().all()

@router.get("/emotional-analytics/", tags=["Placeholders"])
async def get_emotional_analytics():
    return {"humor_medio": "estável"}
