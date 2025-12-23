from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db
from database.repositories.protocolo_repo import ProtocoloRepository
from schemas import ProtocoloResponse, ProtocoloCreate, MessageResponse
from typing import List

router = APIRouter()

@router.get("/{idoso_id}", response_model=ProtocoloResponse)
async def get_active_protocol(idoso_id: int, db: AsyncSession = Depends(get_db)):
    repo = ProtocoloRepository(db)
    protocolo = await repo.get_active_protocol(idoso_id)
    if not protocolo:
        raise HTTPException(status_code=404, detail="No active protocol found for this elder")
    return protocolo

@router.post("/", response_model=ProtocoloResponse)
async def create_protocol(data: ProtocoloCreate, db: AsyncSession = Depends(get_db)):
    repo = ProtocoloRepository(db)
    # Create protocol
    protocolo = await repo.create_protocolo(data.idoso_id, data.nome)
    # Add steps
    for etapa_data in data.etapas:
        await repo.add_etapa(protocolo.id, etapa_data.model_dump())
    
    await db.refresh(protocolo)
    return protocolo

@router.delete("/{protocolo_id}")
async def delete_protocolo(protocolo_id: int, db: AsyncSession = Depends(get_db)):
    # Simple delete (could be a soft delete or repository implementation)
    from database.models import ProtocoloAlerta
    from sqlalchemy import delete
    
    query = delete(ProtocoloAlerta).where(ProtocoloAlerta.id == protocolo_id)
    await db.execute(query)
    await db.commit()
    return {"message": "Protocol deleted"}
