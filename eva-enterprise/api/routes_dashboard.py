"""
Dashboard Routes - Monitoramento em Tempo Real
Métricas de Health Triage, A/B Testing, Imagens Médicas e Epidemiologia
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Dict, Any
from database.connection import get_db

router = APIRouter()

# ==========================================
# HEALTH TRIAGE METRICS
# ==========================================

@router.get("/dashboard/health-triage")
async def get_health_triage_metrics(db: AsyncSession = Depends(get_db)):
    """
    Retorna métricas de triagem de saúde (Thinking Mode)
    """
    query = text("""
        SELECT 
            COUNT(*) as total_analises,
            COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '24 hours') as hoje,
            COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '7 days') as semana,
            COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '30 days') as mes,
            COUNT(*) FILTER (WHERE risk_level = 'CRÍTICO') as criticos,
            COUNT(*) FILTER (WHERE risk_level = 'ALTO') as altos,
            COUNT(*) FILTER (WHERE risk_level = 'MÉDIO') as medios,
            COUNT(*) FILTER (WHERE risk_level = 'BAIXO') as baixos,
            COUNT(*) FILTER (WHERE caregiver_notified = true) as notificados,
            AVG(EXTRACT(EPOCH FROM (notified_at - created_at))) FILTER (WHERE notified_at IS NOT NULL) as tempo_medio_notificacao_seg
        FROM health_thinking_audit
        WHERE created_at >= NOW() - INTERVAL '30 days'
    """)
    
    result = await db.execute(query)
    row = result.fetchone()
    
    if not row:
        return {
            "total_analises": 0,
            "hoje": 0,
            "semana": 0,
            "mes": 0,
            "criticos": 0,
            "altos": 0,
            "medios": 0,
            "baixos": 0,
            "notificados": 0,
            "tempo_medio_notificacao_seg": 0
        }
    
    return {
        "total_analises": row[0] or 0,
        "hoje": row[1] or 0,
        "semana": row[2] or 0,
        "mes": row[3] or 0,
        "criticos": row[4] or 0,
        "altos": row[5] or 0,
        "medios": row[6] or 0,
        "baixos": row[7] or 0,
        "notificados": row[8] or 0,
        "tempo_medio_notificacao_seg": float(row[9]) if row[9] else 0
    }


# ==========================================
# A/B TESTING METRICS
# ==========================================

@router.get("/dashboard/ab-testing")
async def get_ab_testing_metrics(db: AsyncSession = Depends(get_db)):
    """
    Retorna resultados de A/B Testing (Thinking Mode vs Normal Mode)
    """
    query = text("""
        SELECT 
            metric_type,
            grupo_a,
            media_a,
            amostras_a,
            grupo_b,
            media_b,
            amostras_b,
            diferenca_percentual,
            vencedor
        FROM v_ab_test_comparison
        WHERE test_name = 'health_triage_mode'
        ORDER BY metric_type
    """)
    
    result = await db.execute(query)
    rows = result.fetchall()
    
    return [
        {
            "metric": row[0],
            "group_a": row[1],
            "mean_a": float(row[2]) if row[2] else 0,
            "samples_a": row[3] or 0,
            "group_b": row[4],
            "mean_b": float(row[5]) if row[5] else 0,
            "samples_b": row[6] or 0,
            "difference_percent": float(row[7]) if row[7] else 0,
            "winner": row[8]
        }
        for row in rows
    ]


# ==========================================
# MEDICAL IMAGES STATISTICS
# ==========================================

@router.get("/dashboard/medical-images")
async def get_medical_image_stats(db: AsyncSession = Depends(get_db)):
    """
    Retorna estatísticas de análise de imagens médicas
    """
    query = text("""
        SELECT 
            image_type,
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE requires_medical_attention = true) as requer_atencao,
            COUNT(*) FILTER (WHERE caregiver_notified = true) as notificados,
            COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '24 hours') as ultimas_24h
        FROM medical_image_analysis
        WHERE created_at >= NOW() - INTERVAL '30 days'
        GROUP BY image_type
        ORDER BY total DESC
    """)
    
    result = await db.execute(query)
    rows = result.fetchall()
    
    return [
        {
            "image_type": row[0],
            "total": row[1] or 0,
            "requer_atencao": row[2] or 0,
            "notificados": row[3] or 0,
            "ultimas_24h": row[4] or 0
        }
        for row in rows
    ]


# ==========================================
# EPIDEMIOLOGICAL DATA
# ==========================================

@router.get("/dashboard/epidemiological")
async def get_epidemiological_data(db: AsyncSession = Depends(get_db)):
    """
    Retorna dados epidemiológicos para heatmap (Malária, TB, COVID, etc)
    """
    query = text("""
        SELECT 
            tipo_caso,
            total_casos,
            casos_graves,
            coordenadas,
            data
        FROM v_epidemiological_heatmap
        ORDER BY data DESC, total_casos DESC
        LIMIT 100
    """)
    
    result = await db.execute(query)
    rows = result.fetchall()
    
    return [
        {
            "tipo_caso": row[0],
            "total_casos": row[1] or 0,
            "casos_graves": row[2] or 0,
            "coordenadas": row[3],  # String no formato "(lat,lng)"
            "data": row[4].isoformat() if row[4] else None
        }
        for row in rows
    ]


# ==========================================
# MALARIA CASES
# ==========================================

@router.get("/dashboard/malaria-cases")
async def get_malaria_cases(db: AsyncSession = Depends(get_db)):
    """
    Retorna casos de malária detectados
    """
    query = text("""
        SELECT 
            id,
            paciente_nome,
            parasitemia,
            especie,
            gravidade,
            ST_AsText(geolocation) as coordenadas,
            data_diagnostico
        FROM v_malaria_cases
        ORDER BY data_diagnostico DESC
        LIMIT 50
    """)
    
    result = await db.execute(query)
    rows = result.fetchall()
    
    return [
        {
            "id": row[0],
            "paciente_nome": row[1],
            "parasitemia": row[2],
            "especie": row[3],
            "gravidade": row[4],
            "coordenadas": row[5],
            "data_diagnostico": row[6].isoformat() if row[6] else None
        }
        for row in rows
    ]


# ==========================================
# TB SCREENING
# ==========================================

@router.get("/dashboard/tb-screening")
async def get_tb_screening(db: AsyncSession = Depends(get_db)):
    """
    Retorna triagens de tuberculose via raio-X
    """
    query = text("""
        SELECT 
            id,
            paciente_nome,
            probabilidade_tb,
            achados,
            requer_confirmacao,
            ST_AsText(geolocation) as coordenadas,
            created_at
        FROM v_tb_screening
        ORDER BY created_at DESC
        LIMIT 50
    """)
    
    result = await db.execute(query)
    rows = result.fetchall()
    
    return [
        {
            "id": row[0],
            "paciente_nome": row[1],
            "probabilidade_tb": row[2],
            "achados": row[3],
            "requer_confirmacao": row[4],
            "coordenadas": row[5],
            "created_at": row[6].isoformat() if row[6] else None
        }
        for row in rows
    ]


# ==========================================
# RAPID TESTS
# ==========================================

@router.get("/dashboard/rapid-tests")
async def get_rapid_tests(db: AsyncSession = Depends(get_db)):
    """
    Retorna resultados de testes rápidos (COVID, HIV, Dengue)
    """
    query = text("""
        SELECT 
            id,
            paciente_nome,
            tipo_teste,
            fabricante,
            resultado,
            confianca,
            ST_AsText(geolocation) as coordenadas,
            created_at
        FROM v_rapid_tests
        ORDER BY created_at DESC
        LIMIT 50
    """)
    
    result = await db.execute(query)
    rows = result.fetchall()
    
    return [
        {
            "id": row[0],
            "paciente_nome": row[1],
            "tipo_teste": row[2],
            "fabricante": row[3],
            "resultado": row[4],
            "confianca": row[5],
            "coordenadas": row[6],
            "created_at": row[7].isoformat() if row[7] else None
        }
        for row in rows
    ]


# ==========================================
# SKIN LESIONS
# ==========================================

@router.get("/dashboard/skin-lesions")
async def get_skin_lesions(db: AsyncSession = Depends(get_db)):
    """
    Retorna lesões cutâneas analisadas (Mpox, melanoma)
    """
    query = text("""
        SELECT 
            id,
            paciente_nome,
            tipo_lesao,
            prob_mpox,
            risco_melanoma,
            gravidade,
            requer_atencao,
            created_at
        FROM v_skin_lesions
        ORDER BY created_at DESC
        LIMIT 50
    """)
    
    result = await db.execute(query)
    rows = result.fetchall()
    
    return [
        {
            "id": row[0],
            "paciente_nome": row[1],
            "tipo_lesao": row[2],
            "prob_mpox": row[3],
            "risco_melanoma": row[4],
            "gravidade": row[5],
            "requer_atencao": row[6],
            "created_at": row[7].isoformat() if row[7] else None
        }
        for row in rows
    ]


# ==========================================
# SYSTEM HEALTH
# ==========================================

@router.get("/dashboard/system-health")
async def get_system_health(db: AsyncSession = Depends(get_db)):
    """
    Retorna métricas de saúde do sistema
    """
    # Contagem de sessões ativas (últimas 24h)
    query_sessions = text("""
        SELECT COUNT(DISTINCT idoso_id) as active_users
        FROM health_thinking_audit
        WHERE created_at >= NOW() - INTERVAL '24 hours'
    """)
    
    result = await db.execute(query_sessions)
    active_users = result.scalar() or 0
    
    # Total de análises hoje
    query_today = text("""
        SELECT COUNT(*) as total_today
        FROM medical_image_analysis
        WHERE created_at >= CURRENT_DATE
    """)
    
    result = await db.execute(query_today)
    total_today = result.scalar() or 0
    
    return {
        "status": "healthy",
        "active_users_24h": active_users,
        "total_analyses_today": total_today,
        "database_connected": True
    }
