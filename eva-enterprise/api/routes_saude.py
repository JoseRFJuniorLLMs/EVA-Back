"""
Rotas para atividade física e sinais vitais (endpoints principais)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from database.connection import get_db
from database.repositories import repository_saude
from schemas import (
    AtividadeCreate, AtividadeResponse, AtividadeBulkCreate,
    SinaisVitaisHealthCreate, SinaisVitaisHealthResponse, SinaisVitaisHealthBulkCreate,
    SonoCreate, SonoResponse,
    MedicaoCorporalCreate, MedicaoCorporalResponse,
    NutricaoCreate, NutricaoResponse,
    CicloMenstrualCreate, CicloMenstrualResponse
)

router = APIRouter()


# =====================================================
# ATIVIDADE FÍSICA
# =====================================================

@router.post("/atividades", response_model=AtividadeResponse, status_code=status.HTTP_201_CREATED, tags=["Atividade"])
async def criar_atividade(
    atividade: AtividadeCreate,
    db: AsyncSession = Depends(get_db)
):
    """Enviar registro de atividade física"""
    return await repository_saude.create_atividade(db, atividade)


@router.post("/atividades/bulk", response_model=List[AtividadeResponse], status_code=status.HTTP_201_CREATED, tags=["Atividade"])
async def criar_atividades_bulk(
    bulk_data: AtividadeBulkCreate,
    db: AsyncSession = Depends(get_db)
):
    """Enviar múltiplos registros de atividade (sincronização offline)"""
    if len(bulk_data.registros) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Máximo de 100 registros por requisição"
        )
    return await repository_saude.create_atividades_bulk(db, bulk_data.registros)


@router.get("/atividades/{cliente_id}", response_model=List[AtividadeResponse], tags=["Atividade"])
async def listar_atividades(
    cliente_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    """Recuperar histórico de atividades com paginação"""
    return await repository_saude.get_atividades_by_usuario(
        db, cliente_id, skip, limit, data_inicio, data_fim
    )


# =====================================================
# SINAIS VITAIS
# =====================================================

@router.post("/sinais-vitais", response_model=SinaisVitaisHealthResponse, status_code=status.HTTP_201_CREATED, tags=["Sinais Vitais"])
async def criar_sinais_vitais(
    sinais: SinaisVitaisHealthCreate,
    db: AsyncSession = Depends(get_db)
):
    """Enviar registro de sinais vitais (BPM, Pressão, SpO2, etc)"""
    return await repository_saude.create_sinais_vitais(db, sinais)


@router.post("/sinais-vitais/bulk", response_model=List[SinaisVitaisHealthResponse], status_code=status.HTTP_201_CREATED, tags=["Sinais Vitais"])
async def criar_sinais_vitais_bulk(
    bulk_data: SinaisVitaisHealthBulkCreate,
    db: AsyncSession = Depends(get_db)
):
    """Enviar múltiplos registros de sinais vitais"""
    if len(bulk_data.registros) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Máximo de 100 registros por requisição"
        )
    return await repository_saude.create_sinais_vitais_bulk(db, bulk_data.registros)


@router.get("/sinais-vitais/{cliente_id}", response_model=List[SinaisVitaisHealthResponse], tags=["Sinais Vitais"])
async def listar_sinais_vitais(
    cliente_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    """Recuperar histórico de sinais vitais com paginação"""
    return await repository_saude.get_sinais_vitais_by_usuario(
        db, cliente_id, skip, limit, data_inicio, data_fim
    )


# =====================================================
# SONO
# =====================================================

@router.post("/sono", response_model=SonoResponse, status_code=status.HTTP_201_CREATED, tags=["Sono"])
async def criar_sono(
    sono: SonoCreate,
    db: AsyncSession = Depends(get_db)
):
    """Registrar sessão de sono"""
    return await repository_saude.create_sono(db, sono)


@router.get("/sono/{cliente_id}", response_model=List[SonoResponse], tags=["Sono"])
async def listar_sono(
    cliente_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Recuperar histórico de sono"""
    return await repository_saude.get_sono_by_usuario(db, cliente_id, skip, limit)


# =====================================================
# MEDIÇÃO CORPORAL
# =====================================================

@router.post("/medicao-corporal", response_model=MedicaoCorporalResponse, status_code=status.HTTP_201_CREATED, tags=["Medição Corporal"])
async def criar_medicao_corporal(
    medicao: MedicaoCorporalCreate,
    db: AsyncSession = Depends(get_db)
):
    """Enviar medição corporal (peso, altura, etc)"""
    return await repository_saude.create_medicao_corporal(db, medicao)


@router.get("/medicao-corporal/{cliente_id}", response_model=List[MedicaoCorporalResponse], tags=["Medição Corporal"])
async def listar_medicoes_corporais(
    cliente_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Recuperar histórico de medições corporais"""
    return await repository_saude.get_medicoes_corporais_by_usuario(db, cliente_id, skip, limit)


# =====================================================
# NUTRIÇÃO
# =====================================================

@router.post("/nutricao", response_model=NutricaoResponse, status_code=status.HTTP_201_CREATED, tags=["Nutrição"])
async def criar_nutricao(
    nutricao: NutricaoCreate,
    db: AsyncSession = Depends(get_db)
):
    """Registrar nutrição e hidratação"""
    return await repository_saude.create_nutricao(db, nutricao)


@router.get("/nutricao/{cliente_id}", response_model=List[NutricaoResponse], tags=["Nutrição"])
async def listar_nutricao(
    cliente_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Recuperar histórico de nutrição"""
    return await repository_saude.get_nutricao_by_usuario(db, cliente_id, skip, limit)


# =====================================================
# CICLO MENSTRUAL
# =====================================================

@router.post("/ciclo-menstrual", response_model=CicloMenstrualResponse, status_code=status.HTTP_201_CREATED, tags=["Ciclo Menstrual"])
async def criar_ciclo_menstrual(
    ciclo: CicloMenstrualCreate,
    db: AsyncSession = Depends(get_db)
):
    """Registrar dados do ciclo menstrual"""
    return await repository_saude.create_ciclo_menstrual(db, ciclo)


@router.get("/ciclo-menstrual/{cliente_id}", response_model=List[CicloMenstrualResponse], tags=["Ciclo Menstrual"])
async def listar_ciclo_menstrual(
    cliente_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Recuperar histórico do ciclo menstrual"""
    return await repository_saude.get_ciclo_menstrual_by_usuario(db, cliente_id, skip, limit)
