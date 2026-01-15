from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete as sql_delete
from database.connection import get_db
from database.ia_service import IAService
from utils.security import require_subscription
from utils.pagination import get_pagination_params, PaginationParams, PaginatedResponse
from schemas import (
    PadraoComportamentoResponse,
    PredicaoEmergenciaResponse,
    PredicaoEmergenciaCreate,
    EmocaoAnaliseRequest,
    EmocaoHistoricoResponse
)
from typing import List, Optional

router = APIRouter()

# ==================== PADRÕES DE COMPORTAMENTO ====================

@router.get("/padroes/{idoso_id}")
async def listar_padroes(
    idoso_id: int,
    ativo: Optional[bool] = True,
    pagination: PaginationParams = Depends(get_pagination_params),
    db: AsyncSession = Depends(get_db)
):
    """Lista padrões de comportamento detectados para um idoso (paginado)"""
    service = IAService(db)
    items, total = await service.get_padroes(
        idoso_id, 
        ativo=ativo,
        offset=pagination.offset,
        limit=pagination.limit
    )
    
    return PaginatedResponse[PadraoComportamentoResponse].create(
        items=items,
        total=total,
        page=pagination.page,
        limit=pagination.limit
    )

@router.post("/padroes/analisar", dependencies=[Depends(require_subscription("diamond"))])
async def analisar_padroes(
    idoso_id: int = Query(..., description="ID do idoso para análise"),
    db: AsyncSession = Depends(get_db)
):
    """
    Dispara análise de padrões para um idoso específico.
    Nota: A análise real é feita pelo worker Go em background.
    """
    service = IAService(db)
    
    # Verificar se idoso existe
    idoso = await service.get_idoso(idoso_id)
    if not idoso:
        raise HTTPException(status_code=404, detail="Idoso não encontrado")
    
    # TODO: Disparar worker Go via API ou fila
    # Por enquanto, retorna mensagem de sucesso
    
    return {
        "message": f"Análise de padrões agendada para {idoso.nome}",
        "idoso_id": idoso_id,
        "status": "agendado"
    }

@router.get("/padroes/detalhes/{id}", response_model=PadraoComportamentoResponse)
async def detalhar_padrao(id: int, db: AsyncSession = Depends(get_db)):
    """Detalhes de um padrão específico"""
    service = IAService(db)
    padrao = await service.get_padrao_by_id(id)
    if not padrao:
        raise HTTPException(status_code=404, detail="Padrão não encontrado")
    return padrao

@router.delete("/padroes/{id}", status_code=204)
async def desativar_padrao(id: int, db: AsyncSession = Depends(get_db)):
    """Desativa um padrão (marca como inativo)"""
    service = IAService(db)
    success = await service.desativar_padrao(id)
    if not success:
        raise HTTPException(status_code=404, detail="Padrão não encontrado")

# ==================== PREDIÇÕES DE EMERGÊNCIA ====================

@router.get("/predicoes/{idoso_id}")
async def listar_predicoes(
    idoso_id: int,
    ativas: Optional[bool] = True,
    pagination: PaginationParams = Depends(get_pagination_params),
    db: AsyncSession = Depends(get_db)
):
    """Lista predições de emergência para um idoso (paginado)"""
    service = IAService(db)
    items, total = await service.get_predicoes(
        idoso_id, 
        ativas=ativas,
        offset=pagination.offset,
        limit=pagination.limit
    )
    
    return PaginatedResponse[PredicaoEmergenciaResponse].create(
        items=items,
        total=total,
        page=pagination.page,
        limit=pagination.limit
    )

@router.post("/predicoes/analisar", dependencies=[Depends(require_subscription("diamond"))])
async def gerar_predicao(
    idoso_id: int = Query(..., description="ID do idoso"),
    db: AsyncSession = Depends(get_db)
):
    """
    Gera nova predição de emergência para um idoso.
    Nota: A predição real é feita pelo worker Go em background.
    """
    service = IAService(db)
    
    # Verificar se idoso existe
    idoso = await service.get_idoso(idoso_id)
    if not idoso:
        raise HTTPException(status_code=404, detail="Idoso não encontrado")
    
    # TODO: Disparar worker Go via API ou fila
    
    return {
        "message": f"Análise de predição agendada para {idoso.nome}",
        "idoso_id": idoso_id,
        "status": "agendado"
    }

@router.patch("/predicoes/{id}/confirmar")
async def confirmar_predicao(
    id: int,
    confirmada: bool = Query(..., description="True se confirmada, False se falso positivo"),
    db: AsyncSession = Depends(get_db)
):
    """Marca predição como confirmada ou falso positivo"""
    service = IAService(db)
    predicao = await service.confirmar_predicao(id, confirmada)
    if not predicao:
        raise HTTPException(status_code=404, detail="Predição não encontrada")
    return predicao

@router.get("/predicoes/detalhes/{id}", response_model=PredicaoEmergenciaResponse)
async def detalhar_predicao(id: int, db: AsyncSession = Depends(get_db)):
    """Detalhes de uma predição específica"""
    service = IAService(db)
    predicao = await service.get_predicao_by_id(id)
    if not predicao:
        raise HTTPException(status_code=404, detail="Predição não encontrada")
    return predicao

# ==================== ANÁLISE DE EMOÇÃO ====================

@router.post("/emocao/analisar-chamada", dependencies=[Depends(require_subscription("gold"))])
async def analisar_emocao_chamada(
    ligacao_id: int = Query(..., description="ID da ligação/histórico"),
    db: AsyncSession = Depends(get_db)
):
    """
    Analisa emoção de uma chamada completa (pós-chamada).
    Usa transcrição e contexto para detectar emoção predominante.
    """
    service = IAService(db)
    
    # Buscar histórico da chamada
    historico = await service.get_historico_chamada(ligacao_id)
    if not historico:
        raise HTTPException(status_code=404, detail="Histórico de chamada não encontrado")
    
    # Analisar emoção baseado na transcrição e sentimento geral
    emocao = await service.analisar_emocao_texto(
        historico.transcricao_resumo,
        historico.sentimento_geral
    )
    
    return {
        "ligacao_id": ligacao_id,
        "idoso_id": historico.idoso_id,
        "emocao_detectada": emocao["emocao"],
        "intensidade": emocao["intensidade"],
        "confianca": emocao["confianca"],
        "detalhes": emocao.get("detalhes", {})
    }

@router.get("/emocao/historico/{idoso_id}")
async def historico_emocoes(
    idoso_id: int,
    dias: int = Query(30, description="Número de dias para buscar histórico"),
    pagination: PaginationParams = Depends(get_pagination_params),
    db: AsyncSession = Depends(get_db)
):
    """Histórico de emoções detectadas nas chamadas (paginado)"""
    service = IAService(db)
    
    # Buscar todas as emoções do período
    all_emocoes = await service.get_historico_emocoes(idoso_id, dias)
    
    # Aplicar paginação manual (já que get_historico_emocoes retorna lista processada)
    total = len(all_emocoes)
    start = pagination.offset
    end = start + pagination.limit
    items = all_emocoes[start:end]
    
    return PaginatedResponse[EmocaoHistoricoResponse].create(
        items=items,
        total=total,
        page=pagination.page,
        limit=pagination.limit
    )

# ==================== INSIGHTS PSICOLÓGICOS ====================

@router.get("/insights/{idoso_id}")
async def listar_insights(
    idoso_id: int,
    tipo: Optional[str] = None,
    pagination: PaginationParams = Depends(get_pagination_params),
    db: AsyncSession = Depends(get_db)
):
    """Lista insights psicológicos para um idoso (paginado)"""
    service = IAService(db)
    
    # Buscar todos os insights
    all_insights = await service.get_insights(idoso_id, tipo)
    
    # Aplicar paginação manual
    total = len(all_insights)
    start = pagination.offset
    end = start + pagination.limit
    items = all_insights[start:end]
    
    return PaginatedResponse.create(
        items=items,
        total=total,
        page=pagination.page,
        limit=pagination.limit
    )

@router.post("/insights/gerar", dependencies=[Depends(require_subscription("gold"))])
async def gerar_insights(
    idoso_id: int = Query(..., description="ID do idoso"),
    db: AsyncSession = Depends(get_db)
):
    """
    Gera novos insights psicológicos baseados em padrões e histórico.
    Usa IA para análise contextual.
    """
    service = IAService(db)
    
    # Verificar se idoso existe
    idoso = await service.get_idoso(idoso_id)
    if not idoso:
        raise HTTPException(status_code=404, detail="Idoso não encontrado")
    
    # Gerar insights baseados em padrões e histórico
    insights = await service.gerar_insights_ia(idoso_id)
    
    return {
        "message": f"Insights gerados para {idoso.nome}",
        "idoso_id": idoso_id,
        "total_insights": len(insights),
        "insights": insights
    }

# ==================== DASHBOARD / RESUMO ====================

@router.get("/dashboard/{idoso_id}")
async def dashboard_ia(idoso_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retorna resumo completo de IA para um idoso:
    - Padrões ativos
    - Predições ativas
    - Últimas emoções
    - Insights recentes
    """
    service = IAService(db)
    
    # Verificar se idoso existe
    idoso = await service.get_idoso(idoso_id)
    if not idoso:
        raise HTTPException(status_code=404, detail="Idoso não encontrado")
    
    # Buscar dados
    padroes = await service.get_padroes(idoso_id, ativo=True)
    predicoes = await service.get_predicoes(idoso_id, ativas=True)
    emocoes = await service.get_historico_emocoes(idoso_id, dias=7)
    insights = await service.get_insights(idoso_id, tipo=None)
    
    return {
        "idoso": {
            "id": idoso.id,
            "nome": idoso.nome
        },
        "padroes_ativos": len(padroes),
        "predicoes_ativas": len(predicoes),
        "predicoes_alto_risco": len([p for p in predicoes if p.nivel_risco in ["alto", "critico"]]),
        "emocao_predominante": service.calcular_emocao_predominante(emocoes),
        "total_insights": len(insights),
        "padroes": padroes[:5],  # Top 5
        "predicoes": predicoes[:3],  # Top 3
        "emocoes_recentes": emocoes[:7],  # Última semana
        "insights_recentes": insights[:5]  # Top 5
    }
