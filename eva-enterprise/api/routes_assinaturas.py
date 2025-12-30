from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db
from database.subscription_service import SubscriptionService
from schemas import SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse
from typing import List

router = APIRouter()

@router.get("/", response_model=List[SubscriptionResponse])
async def listar_assinaturas(db: AsyncSession = Depends(get_db)):
    """Lista todas as assinaturas"""
    service = SubscriptionService(db)
    return await service.get_all()

@router.get("/{id}", response_model=SubscriptionResponse)
async def obter_assinatura(id: int, db: AsyncSession = Depends(get_db)):
    """Obtém assinatura por ID"""
    service = SubscriptionService(db)
    sub = await service.get_by_id(id)
    if not sub:
        raise HTTPException(status_code=404, detail="Assinatura não encontrada")
    return sub

@router.get("/entidade/{nome}", response_model=SubscriptionResponse)
async def obter_por_entidade(nome: str, db: AsyncSession = Depends(get_db)):
    """Obtém assinatura ativa por nome da entidade"""
    service = SubscriptionService(db)
    sub = await service.get_active_by_entity(nome)
    if not sub:
        raise HTTPException(status_code=404, detail="Assinatura não encontrada")
    return sub

@router.post("/", response_model=SubscriptionResponse, status_code=201)
async def criar_assinatura(
    data: SubscriptionCreate, 
    db: AsyncSession = Depends(get_db)
):
    """Cria nova assinatura"""
    service = SubscriptionService(db)
    return await service.create(data)

@router.put("/{id}", response_model=SubscriptionResponse)
async def atualizar_assinatura(
    id: int, 
    data: SubscriptionUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """Atualiza assinatura"""
    service = SubscriptionService(db)
    sub = await service.update(id, data)
    if not sub:
        raise HTTPException(status_code=404, detail="Assinatura não encontrada")
    return sub

@router.patch("/{id}/status")
async def alterar_status(
    id: int, 
    status: str = Query(..., regex="^(ativo|cancelado|suspenso|pendente)$"),
    db: AsyncSession = Depends(get_db)
):
    """Altera status da assinatura (ativo/cancelado/suspenso/pendente)"""
    service = SubscriptionService(db)
    result = await service.update_status(id, status)
    if not result:
        raise HTTPException(status_code=404, detail="Assinatura não encontrada")
    return result

@router.delete("/{id}", status_code=204)
async def excluir_assinatura(id: int, db: AsyncSession = Depends(get_db)):
    """Exclui uma assinatura"""
    service = SubscriptionService(db)
    success = await service.delete(id)
    if not success:
        raise HTTPException(status_code=404, detail="Assinatura não encontrada")

@router.get("/{id}/features")
async def obter_features(id: int, db: AsyncSession = Depends(get_db)):
    """Lista features disponíveis no plano da assinatura"""
    service = SubscriptionService(db)
    features = await service.get_features(id)
    if features is None:
        raise HTTPException(status_code=404, detail="Assinatura não encontrada")
    return {"features": features}

@router.get("/{id}/consumo")
async def obter_consumo(id: int, db: AsyncSession = Depends(get_db)):
    """Obtém consumo de minutos"""
    service = SubscriptionService(db)
    usage = await service.get_usage(id)
    if usage is None:
        raise HTTPException(status_code=404, detail="Assinatura não encontrada")
    return usage

@router.post("/{id}/consumir")
async def consumir_minutos(
    id: int, 
    minutos: int = Query(..., gt=0, description="Quantidade de minutos a consumir"),
    db: AsyncSession = Depends(get_db)
):
    """Registra consumo de minutos"""
    service = SubscriptionService(db)
    try:
        usage = await service.consume_minutes(id, minutos)
        return usage
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consumir minutos: {str(e)}")
