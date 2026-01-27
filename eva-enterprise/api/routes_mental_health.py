"""
Rotas FastAPI para Sistema de Saúde Mental
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, date, timedelta
import logging

from database.connection import get_db
from database.repositories.mental_health_repository import MentalHealthRepository
from api.schemas.mental_health_schemas import (
    AssessmentCreate, AssessmentResponse, AssessmentTrend,
    MoodDiaryCreate, MoodDiaryResponse, MoodStatistics,
    CrisisEventCreate, CrisisEventResponse,
    SafetyPlanCreate, SafetyPlanResponse,
    NLPAnalysisCreate, SentimentTrend,
    MLPredictionCreate, MLPredictionResponse,
    PatientMentalHealthSummary,
    ScaleReference,
    ScaleType, RiskLevel
)

router = APIRouter(prefix="/api/v1/mental-health", tags=["Dashboard - Saude Mental"])
logger = logging.getLogger(__name__)


# =====================================================================
# ASSESSMENTS (Avaliações Clínicas)
# =====================================================================

@router.post("/assessments", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assessment(
    assessment_data: AssessmentCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Criar nova avaliação clínica (PHQ-9, GAD-7, C-SSRS, etc)

    **Escalas suportadas:**
    - **PHQ9**: Patient Health Questionnaire (Depressão) - 0-27 pontos
    - **GAD7**: Generalized Anxiety Disorder (Ansiedade) - 0-21 pontos
    - **C-SSRS**: Columbia-Suicide Severity Rating Scale (Risco Suicida) - 0-6 pontos
    - **PSS10**: Perceived Stress Scale (Estresse) - 0-40 pontos
    - **Y-BOCS**: Yale-Brown OCD Scale (TOC) - 0-40 pontos
    - **PCL5**: PTSD Checklist (PTSD) - 0-80 pontos
    """
    try:
        # Calcular score total
        score = sum([qa.score for qa in assessment_data.questions_answers])

        # Determinar severidade baseado no tipo de escala
        severity_level = _calculate_severity(assessment_data.scale_type, score)

        # Gerar interpretação
        interpretation = _generate_interpretation(assessment_data.scale_type, score, severity_level)

        # Criar avaliação
        assessment = await MentalHealthRepository.create_assessment(
            session=db,
            patient_id=assessment_data.patient_id,
            scale_type=assessment_data.scale_type.value,
            score=score,
            severity_level=severity_level,
            questions_answers=[qa.dict() for qa in assessment_data.questions_answers],
            professional_id=assessment_data.professional_id,
            notes=assessment_data.notes,
            interpretation=interpretation
        )

        # Se C-SSRS com score >= 3, acionar protocolo de emergência
        if assessment_data.scale_type == ScaleType.C_SSRS and score >= 3:
            logger.critical(f"🚨 ALERTA C-SSRS: Score {score} - Paciente {assessment_data.patient_id}")
            # TODO: Acionar protocolo de emergência

        return assessment

    except Exception as e:
        logger.error(f"Erro ao criar avaliação: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/assessments/{patient_id}/latest/{scale_type}", response_model=Optional[AssessmentResponse])
async def get_latest_assessment(
    patient_id: int,
    scale_type: ScaleType,
    db: AsyncSession = Depends(get_db)
):
    """Buscar última avaliação de um tipo específico"""
    assessment = await MentalHealthRepository.get_latest_assessment_by_type(
        db, patient_id, scale_type.value
    )
    return assessment


@router.get("/assessments/{patient_id}/history/{scale_type}", response_model=List[AssessmentResponse])
async def get_assessment_history(
    patient_id: int,
    scale_type: ScaleType,
    days: int = 90,
    db: AsyncSession = Depends(get_db)
):
    """Buscar histórico de avaliações"""
    assessments = await MentalHealthRepository.get_assessment_history(
        db, patient_id, scale_type.value, days
    )
    return assessments


@router.get("/assessments/{patient_id}/trend/{scale_type}", response_model=AssessmentTrend)
async def get_assessment_trend(
    patient_id: int,
    scale_type: ScaleType,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Calcular tendência de scores (melhorando/piorando/estável)"""
    trend = await MentalHealthRepository.get_assessment_trend(
        db, patient_id, scale_type.value, limit
    )
    return trend


# =====================================================================
# MOOD DIARY (Diário de Humor)
# =====================================================================

@router.post("/mood-diary", response_model=MoodDiaryResponse, status_code=status.HTTP_201_CREATED)
async def create_mood_entry(
    mood_data: MoodDiaryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Criar entrada no diário de humor (manhã, tarde ou noite)"""
    try:
        mood_entry = await MentalHealthRepository.create_mood_entry(
            session=db,
            patient_id=mood_data.patient_id,
            date=mood_data.date,
            time_of_day=mood_data.time_of_day.value,
            mood_score=mood_data.mood_score,
            anxiety_level=mood_data.anxiety_level,
            energy_level=mood_data.energy_level,
            sleep_quality=mood_data.sleep_quality,
            sleep_hours=mood_data.sleep_hours,
            awakenings=mood_data.awakenings,
            notes=mood_data.notes,
            symptoms=mood_data.symptoms,
            triggers=mood_data.triggers,
            helpful_activities=mood_data.helpful_activities,
            physical_symptoms=mood_data.physical_symptoms,
            intrusive_thoughts=mood_data.intrusive_thoughts,
            intrusive_thoughts_description=mood_data.intrusive_thoughts_description,
            accomplished_planned_activities=mood_data.accomplished_planned_activities
        )

        # Alerta se humor muito baixo persistente
        if mood_data.mood_score and mood_data.mood_score <= 3:
            logger.warning(f"⚠️ Humor muito baixo: {mood_data.mood_score} - Paciente {mood_data.patient_id}")

        return mood_entry

    except Exception as e:
        logger.error(f"Erro ao criar entrada de humor: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mood-diary/{patient_id}/history", response_model=List[MoodDiaryResponse])
async def get_mood_history(
    patient_id: int,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Buscar histórico de humor"""
    entries = await MentalHealthRepository.get_mood_history(db, patient_id, days)
    return entries


@router.get("/mood-diary/{patient_id}/statistics", response_model=MoodStatistics)
async def get_mood_statistics(
    patient_id: int,
    days: int = 7,
    db: AsyncSession = Depends(get_db)
):
    """Calcular estatísticas de humor"""
    stats = await MentalHealthRepository.get_mood_statistics(db, patient_id, days)
    return stats


# =====================================================================
# CRISIS EVENTS (Eventos de Crise)
# =====================================================================

@router.post("/crisis-events", response_model=CrisisEventResponse, status_code=status.HTTP_201_CREATED)
async def create_crisis_event(
    crisis_data: CrisisEventCreate,
    db: AsyncSession = Depends(get_db)
):
    """Registrar evento de crise"""
    try:
        crisis = await MentalHealthRepository.create_crisis_event(
            session=db,
            patient_id=crisis_data.patient_id,
            crisis_type=crisis_data.crisis_type.value,
            severity=crisis_data.severity.value,
            occurred_at=crisis_data.occurred_at,
            duration_minutes=crisis_data.duration_minutes,
            location=crisis_data.location,
            precipitating_factors=crisis_data.precipitating_factors,
            warning_signs=crisis_data.warning_signs,
            intervention_taken=crisis_data.intervention_taken,
            emergency_contacts_notified=crisis_data.emergency_contacts_notified,
            hospitalization_required=crisis_data.hospitalization_required,
            hospital_name=crisis_data.hospital_name,
            notes=crisis_data.notes
        )

        # Acionar protocolo de emergência se tentativa de suicídio
        if crisis_data.crisis_type.value == "suicide_attempt":
            logger.critical(f"🚨🚨 TENTATIVA DE SUICÍDIO REGISTRADA - Paciente {crisis_data.patient_id}")
            # TODO: Acionar protocolo de emergência imediatamente

        return crisis

    except Exception as e:
        logger.error(f"Erro ao registrar crise: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/crisis-events/{patient_id}/recent", response_model=List[CrisisEventResponse])
async def get_recent_crises(
    patient_id: int,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Buscar crises recentes"""
    crises = await MentalHealthRepository.get_recent_crises(db, patient_id, days)
    return crises


# =====================================================================
# SAFETY PLANS (Planos de Segurança)
# =====================================================================

@router.post("/safety-plans", response_model=SafetyPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_safety_plan(
    safety_plan_data: SafetyPlanCreate,
    db: AsyncSession = Depends(get_db)
):
    """Criar plano de segurança anti-suicídio"""
    try:
        safety_plan = await MentalHealthRepository.create_safety_plan(
            session=db,
            patient_id=safety_plan_data.patient_id,
            created_by=safety_plan_data.created_by,
            warning_signs=safety_plan_data.warning_signs,
            internal_coping_strategies=safety_plan_data.internal_coping_strategies,
            people_to_contact=[p.dict() for p in safety_plan_data.people_to_contact],
            professionals_to_contact=[p.dict() for p in safety_plan_data.professionals_to_contact],
            crisis_hotlines=[h.dict() for h in safety_plan_data.crisis_hotlines],
            social_distractions=safety_plan_data.social_distractions,
            environment_safety=safety_plan_data.environment_safety,
            reasons_for_living=safety_plan_data.reasons_for_living
        )

        return safety_plan

    except Exception as e:
        logger.error(f"Erro ao criar plano de segurança: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/safety-plans/{patient_id}/active", response_model=Optional[SafetyPlanResponse])
async def get_active_safety_plan(
    patient_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Buscar plano de segurança ativo"""
    safety_plan = await MentalHealthRepository.get_active_safety_plan(db, patient_id)
    return safety_plan


# =====================================================================
# NLP ANALYSIS (Análise de Conversas)
# =====================================================================

@router.post("/nlp-analysis", status_code=status.HTTP_201_CREATED)
async def create_nlp_analysis(
    nlp_data: NLPAnalysisCreate,
    db: AsyncSession = Depends(get_db)
):
    """Criar análise NLP de conversa"""
    try:
        analysis = await MentalHealthRepository.create_nlp_analysis(
            session=db,
            patient_id=nlp_data.patient_id,
            sentiment_score=nlp_data.sentiment_score,
            sentiment_label=nlp_data.sentiment_label,
            detected_keywords=nlp_data.detected_keywords,
            danger_flags=nlp_data.danger_flags,
            conversation_session_id=nlp_data.conversation_session_id,
            message_id=nlp_data.message_id,
            extracted_entities=nlp_data.extracted_entities,
            topic_classification=nlp_data.topic_classification
        )

        return {"message": "Análise NLP criada com sucesso", "id": analysis.id}

    except Exception as e:
        logger.error(f"Erro ao criar análise NLP: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/nlp-analysis/{patient_id}/sentiment-trend", response_model=SentimentTrend)
async def get_sentiment_trend(
    patient_id: int,
    days: int = 7,
    db: AsyncSession = Depends(get_db)
):
    """Calcular tendência de sentimento nas conversas"""
    trend = await MentalHealthRepository.get_recent_sentiment_trend(db, patient_id, days)
    return trend


# =====================================================================
# ML PREDICTIONS (Predições de Machine Learning)
# =====================================================================

@router.post("/ml-predictions", response_model=MLPredictionResponse, status_code=status.HTTP_201_CREATED)
async def create_ml_prediction(
    prediction_data: MLPredictionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Criar predição de modelo de ML"""
    try:
        prediction = await MentalHealthRepository.create_ml_prediction(
            session=db,
            patient_id=prediction_data.patient_id,
            model_name=prediction_data.model_name,
            prediction_type=prediction_data.prediction_type,
            prediction_value=prediction_data.prediction_value,
            prediction_label=prediction_data.prediction_label,
            confidence_score=prediction_data.confidence_score,
            features_used=prediction_data.features_used,
            valid_until=prediction_data.valid_until
        )

        return prediction

    except Exception as e:
        logger.error(f"Erro ao criar predição ML: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ml-predictions/{patient_id}/latest/{prediction_type}", response_model=Optional[MLPredictionResponse])
async def get_latest_prediction(
    patient_id: int,
    prediction_type: str,
    db: AsyncSession = Depends(get_db)
):
    """Buscar última predição válida"""
    prediction = await MentalHealthRepository.get_latest_prediction(
        db, patient_id, prediction_type
    )
    return prediction


# =====================================================================
# PATIENT SUMMARY (Resumo do Paciente)
# =====================================================================

@router.get("/summary/{patient_id}", response_model=PatientMentalHealthSummary)
async def get_patient_summary(
    patient_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Obter resumo completo de saúde mental do paciente

    Inclui:
    - Últimas avaliações (PHQ-9, GAD-7, C-SSRS)
    - Estatísticas de humor (7 dias)
    - Tendência de sentimento (7 dias)
    - Contagem de crises (30 dias)
    - Plano de segurança ativo
    - Nível de risco geral
    """
    summary = await MentalHealthRepository.get_patient_mental_health_summary(db, patient_id)
    return summary


# =====================================================================
# SCALE REFERENCES (Escalas de Referência)
# =====================================================================

@router.get("/scales/{scale_type}", response_model=ScaleReference)
async def get_scale_reference(
    scale_type: ScaleType,
    language: str = 'pt-BR',
    db: AsyncSession = Depends(get_db)
):
    """Buscar questões de uma escala de avaliação"""
    scale = await MentalHealthRepository.get_scale_reference(db, scale_type.value, language)

    if not scale:
        raise HTTPException(
            status_code=404,
            detail=f"Escala {scale_type.value} não encontrada para o idioma {language}"
        )

    return scale


# =====================================================================
# HELPER FUNCTIONS
# =====================================================================

def _calculate_severity(scale_type: ScaleType, score: int) -> str:
    """Calcular severidade baseado no tipo de escala e score"""

    severity_ranges = {
        ScaleType.PHQ9: {
            (0, 4): "minimal",
            (5, 9): "mild",
            (10, 14): "moderate",
            (15, 19): "moderately_severe",
            (20, 27): "severe"
        },
        ScaleType.GAD7: {
            (0, 4): "minimal",
            (5, 9): "mild",
            (10, 14): "moderate",
            (15, 21): "severe"
        },
        ScaleType.C_SSRS: {
            (0, 0): "minimal",
            (1, 1): "mild",
            (2, 2): "moderate",
            (3, 4): "severe",
            (5, 6): "extremely_severe"
        },
        ScaleType.PSS10: {
            (0, 13): "minimal",
            (14, 26): "moderate",
            (27, 40): "severe"
        }
    }

    ranges = severity_ranges.get(scale_type, {})

    for (min_score, max_score), severity in ranges.items():
        if min_score <= score <= max_score:
            return severity

    return "unknown"


def _generate_interpretation(scale_type: ScaleType, score: int, severity: str) -> str:
    """Gerar interpretação textual do resultado"""

    interpretations = {
        ScaleType.PHQ9: {
            "minimal": "Mínima ou nenhuma depressão. Sintomas não clinicamente significativos.",
            "mild": "Depressão leve. Monitoramento recomendado.",
            "moderate": "Depressão moderada. Considerar tratamento psicoterapêutico.",
            "moderately_severe": "Depressão moderadamente grave. Tratamento psicoterapêutico e/ou farmacológico recomendado.",
            "severe": "Depressão grave. Tratamento farmacológico e psicoterapêutico necessário. Avaliar risco suicida."
        },
        ScaleType.GAD7: {
            "minimal": "Ansiedade mínima. Sintomas não clinicamente significativos.",
            "mild": "Ansiedade leve. Técnicas de manejo de estresse recomendadas.",
            "moderate": "Ansiedade moderada. Considerar tratamento psicoterapêutico.",
            "severe": "Ansiedade grave. Tratamento psicoterapêutico e/ou farmacológico necessário."
        },
        ScaleType.C_SSRS: {
            "minimal": "Sem risco suicida identificado.",
            "mild": "Ideação passiva de morte. Monitoramento necessário.",
            "moderate": "Ideação suicida ativa sem plano. Agendamento de consulta urgente.",
            "severe": "Ideação suicida com plano ou intenção. Intervenção imediata necessária.",
            "extremely_severe": "Comportamento suicida recente. EMERGÊNCIA - Acionar protocolo de crise."
        }
    }

    default_interpretation = f"Score: {score} - Severidade: {severity}"

    return interpretations.get(scale_type, {}).get(severity, default_interpretation)
