from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db
from database.repositories.pagamento_repo import PagamentoRepository, AuditRepository
from schemas import (
    PagamentoResponse, PagamentoCreate, AuditLogResponse
)
from typing import List

router = APIRouter()


# --- Audit Logs ---

@router.get("/audit-logs/", response_model=List[AuditLogResponse])
async def list_audit_logs(usuario: str = None, limit: int = 50, db: AsyncSession = Depends(get_db)):
    repo = AuditRepository(db)
    return await repo.get_logs(limit=limit, usuario=usuario)

@router.get("/audit-logs/{id}", response_model=AuditLogResponse)
async def get_audit_log(id: int, db: AsyncSession = Depends(get_db)):
    repo = AuditRepository(db)
    log = await repo.get_by_id(id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log

# --- Pagamentos ---

@router.get("/", response_model=List[PagamentoResponse])
async def list_pagamentos(status: str = None, limit: int = 50, db: AsyncSession = Depends(get_db)):
    repo = PagamentoRepository(db)
    return await repo.get_pagamentos(limit=limit, status=status)

@router.post("/", response_model=PagamentoResponse)
async def create_pagamento(pagamento: PagamentoCreate, db: AsyncSession = Depends(get_db)):
    repo = PagamentoRepository(db)
    return await repo.create_pagamento(pagamento.model_dump())

@router.get("/{id}", response_model=PagamentoResponse)
async def get_pagamento(id: int, db: AsyncSession = Depends(get_db)):
    repo = PagamentoRepository(db)
    pag = await repo.get_by_id(id)
    if not pag:
        raise HTTPException(status_code=404, detail="Pagamento not found")
    return pag

