"""
Endpoints opcionais que ainda não foram implementados.
Retornam arrays/objetos vazios para evitar 404 no frontend.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db
from utils.security import get_current_user

router = APIRouter()


@router.get("/metricas-analytics/")
async def get_metricas_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Métricas e analytics - TODO: implementar"""
    return {
        "total_usuarios": 0,
        "total_idosos": 0,
        "total_chamadas": 0,
        "tempo_medio_atendimento": 0
    }


@router.get("/audit-logs/")
async def get_audit_logs(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Logs de auditoria - TODO: implementar"""
    return []


@router.get("/timeline-data/")
async def get_timeline_data(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Dados de timeline - TODO: implementar"""
    return []


@router.get("/pagamentos/")
async def get_pagamentos(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Pagamentos - TODO: implementar"""
    return []


@router.get("/biografia-idosos/")
async def get_biografia_idosos(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Biografias dos idosos - TODO: implementar"""
    return []


@router.get("/dados-finops/")
async def get_dados_finops(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Dados financeiros e operacionais - TODO: implementar"""
    return {
        "receita_mensal": 0,
        "despesas_mensais": 0,
        "lucro_liquido": 0,
        "projecao_anual": 0
    }


@router.get("/insight-eva/")
async def get_insight_eva(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Insights da EVA - TODO: implementar"""
    return {
        "insights": [],
        "recomendacoes": [],
        "alertas": []
    }
