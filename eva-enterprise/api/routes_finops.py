from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db
from database.repositories.faturamento_repo import FaturamentoRepository
from typing import Optional
import datetime

router = APIRouter()

@router.get("/")
async def get_finops_stats(
    mes: Optional[int] = None, 
    ano: Optional[int] = None, 
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna estatísticas globais de FinOps para o dashboard.
    Se mês/ano não informados, usa o atual.
    """
    now = datetime.datetime.now()
    if mes is None: mes = now.month
    if ano is None: ano = now.year
    
    repo = FaturamentoRepository(db)
    try:
        stats = await repo.get_global_finops_stats(mes, ano)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
