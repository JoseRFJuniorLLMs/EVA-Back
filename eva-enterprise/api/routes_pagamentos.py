from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db
from database.repositories.faturamento_repo import FaturamentoRepository
from schemas import AssinaturaResponse, ConsumoResponse, MessageResponse
from typing import List, Optional

router = APIRouter()

@router.get("/assinaturas", response_model=List[AssinaturaResponse])
async def list_assinaturas(db: AsyncSession = Depends(get_db)):
    repo = FaturamentoRepository(db)
    return await repo.list_assinaturas()

@router.get("/assinaturas/{id}", response_model=AssinaturaResponse)
async def get_assinatura(id: int, db: AsyncSession = Depends(get_db)):
    repo = FaturamentoRepository(db)
    assinatura = await repo.get_assinatura(id)
    if not assinatura:
        raise HTTPException(status_code=404, detail="Assinatura not found")
    return assinatura

@router.get("/consumo/{idoso_id}", response_model=ConsumoResponse)
async def get_consumo(
    idoso_id: int, 
    mes: Optional[int] = None, 
    ano: Optional[int] = None, 
    db: AsyncSession = Depends(get_db)
):
    """Obtém o consumo de um idoso. Se mês/ano não informados, usa o atual."""
    import datetime
    now = datetime.datetime.now()
    if mes is None: mes = now.month
    if ano is None: ano = now.year
    
    repo = FaturamentoRepository(db)
    consumo = await repo.get_consumo_mes(idoso_id, mes, ano)
    if not consumo:
         raise HTTPException(status_code=404, detail="Consumo não encontrado para este período")
    return consumo

@router.get("/audit", response_model=List[dict])
async def list_audit_logs(db: AsyncSession = Depends(get_db)):
    # Simple query for audit logs
    from database.models import AuditLog
    from sqlalchemy import select
    query = select(AuditLog).order_by(AuditLog.criado_em.desc()).limit(10)
    result = await db.execute(query)
    return [
        {
            "id": log.id,
            "usuario": log.usuario_email,
            "acao": log.acao,
            "data": log.criado_em
        } for log in result.scalars().all()
    ]
