"""
Rotas para dashboard e relatórios analíticos
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from database.connection import get_db
from database.repositories import repository_saude
from schemas import DashboardResumoResponse, RelatorioMensalResponse

router = APIRouter()


@router.get("/dashboard/resumo-diario/{cliente_id}", response_model=DashboardResumoResponse)
async def obter_resumo_diario(
    cliente_id: int,
    data: date = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Resumo diário para dashboard
    
    Retorna compilado de:
    - Passos hoje
    - Último BPM registrado
    - Última pressão arterial
    - Horas de sono (ontem)
    - Calorias consumidas hoje
    - Água ingerida hoje (ml)
    """
    if data is None:
        data = date.today()
    
    resumo = await repository_saude.get_dashboard_resumo(db, cliente_id, data)
    return resumo


@router.get("/relatorios/mensal/{cliente_id}", response_model=RelatorioMensalResponse)
async def obter_relatorio_mensal(
    cliente_id: int,
    mes: int,
    ano: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Relatório mensal para análise de tendências
    
    Retorna:
    - Total de passos no mês
    - Média de BPM
    - Média de horas de sono
    - Peso inicial e final do mês
    - Total de atividades registradas
    """
    if mes < 1 or mes > 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mês deve estar entre 1 e 12"
        )
    
    if ano < 2000 or ano > 2100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ano inválido"
        )
    
    relatorio = await repository_saude.get_relatorio_mensal(db, cliente_id, mes, ano)
    return relatorio
