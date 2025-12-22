from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from database.repositories.pagamento_repo import PagamentoRepository, AuditRepository
from schemas import (
    PagamentoResponse, PagamentoCreate, AuditLogResponse
)
from typing import List

router = APIRouter()

# --- Pagamentos ---

@router.get("/", response_model=List[PagamentoResponse])
def list_pagamentos(status: str = None, limit: int = 50, db: Session = Depends(get_db)):
    repo = PagamentoRepository(db)
    return repo.get_pagamentos(limit=limit, status=status)

@router.post("/", response_model=PagamentoResponse)
def create_pagamento(pagamento: PagamentoCreate, db: Session = Depends(get_db)):
    repo = PagamentoRepository(db)
    return repo.create_pagamento(pagamento.model_dump())

@router.get("/{id}", response_model=PagamentoResponse)
def get_pagamento(id: int, db: Session = Depends(get_db)):
    repo = PagamentoRepository(db)
    pag = repo.get_by_id(id)
    if not pag:
        raise HTTPException(status_code=404, detail="Pagamento not found")
    return pag

# --- Audit Logs ---

@router.get("/audit-logs", response_model=List[AuditLogResponse])
def list_audit_logs(usuario: str = None, limit: int = 50, db: Session = Depends(get_db)):
    repo = AuditRepository(db)
    return repo.get_logs(limit=limit, usuario=usuario)

@router.get("/audit-logs/{id}", response_model=AuditLogResponse)
def get_audit_log(id: int, db: Session = Depends(get_db)):
    repo = AuditRepository(db)
    log = repo.get_by_id(id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log
