from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db
from database.repositories.protocolo_repo import ProtocoloRepository
from schemas import (
    ProtocoloResponse, ProtocoloCreate, ProtocoloEtapaResponse, ProtocoloEtapaCreate, MessageResponse
)
from typing import List

router = APIRouter()

@router.get("/{idoso_id}", response_model=List[ProtocoloResponse])
async def list_protocolos(idoso_id: int, db: AsyncSession = Depends(get_db)):
    """Lista todos os protocolos de um idoso.
    Regra: Retorna lista limitada a 1 se muitos filtros forem usados (seguindo padrão)."""
    repo = ProtocoloRepository(db)
    protocolos = await repo.get_by_idoso(idoso_id)
    
    # Enrich with stages
    results = []
    for p in protocolos:
        etapas = await repo.get_etapas(p.id)
        results.append(ProtocoloResponse(
            id=p.id,
            idoso_id=p.idoso_id,
            nome=p.nome,
            ativo=p.ativo,
            etapas=[ProtocoloEtapaResponse.model_validate(e) for e in etapas]
        ))
    return results

@router.post("/", response_model=ProtocoloResponse)
async def create_protocolo(data: ProtocoloCreate, db: AsyncSession = Depends(get_db)):
    """Cria um novo protocolo e suas etapas iniciais"""
    repo = ProtocoloRepository(db)
    protocolo = await repo.create_protocolo(idoso_id=data.idoso_id, nome=data.nome)
    
    etapas_response = []
    for e_data in data.etapas:
        etapa = await repo.add_etapa(protocolo.id, e_data.model_dump())
        etapas_response.append(ProtocoloEtapaResponse.model_validate(etapa))
        
    return ProtocoloResponse(
        id=protocolo.id,
        idoso_id=protocolo.idoso_id,
        nome=protocolo.nome,
        ativo=protocolo.ativo,
        etapas=etapas_response
    )

@router.post("/{protocolo_id}/etapas", response_model=ProtocoloEtapaResponse)
async def add_etapa(protocolo_id: int, data: ProtocoloEtapaCreate, db: AsyncSession = Depends(get_db)):
    """Adiciona uma etapa a um protocolo existente"""
    repo = ProtocoloRepository(db)
    etapa = await repo.add_etapa(protocolo_id, data.model_dump())
    return ProtocoloEtapaResponse.model_validate(etapa)

@router.delete("/etapas/{etapa_id}", response_model=MessageResponse)
async def delete_etapa(etapa_id: int, db: AsyncSession = Depends(get_db)):
    """Remove uma etapa de protocolo"""
    repo = ProtocoloRepository(db)
    success = await repo.delete_etapa(etapa_id)
    if not success:
        raise HTTPException(status_code=404, detail="Etapa não encontrada")
    return {"message": "Etapa removida com sucesso"}
