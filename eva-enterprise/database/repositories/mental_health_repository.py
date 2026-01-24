"""
Repositório para operações de banco de dados relacionadas à saúde mental
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import logging

from ..models import (
    MentalHealthAssessment,
    MoodDiary,
    MentalHealthCondition,
    Symptom,
    Trigger,
    TherapySession,
    CrisisEvent,
    SafetyPlan,
    MedicationSideEffect,
    NLPConversationAnalysis,
    MLPrediction,
    TreatmentGoal,
    AssessmentScaleReference,
    Idoso
)

logger = logging.getLogger(__name__)


class MentalHealthRepository:
    """Repositório para gerenciamento de dados de saúde mental"""

    # ===============================================================
    # MENTAL HEALTH ASSESSMENTS (PHQ-9, GAD-7, C-SSRS, etc)
    # ===============================================================

    @staticmethod
    async def create_assessment(
        session: AsyncSession,
        patient_id: int,
        scale_type: str,
        score: int,
        severity_level: str,
        questions_answers: List[Dict],
        professional_id: Optional[int] = None,
        notes: Optional[str] = None,
        interpretation: Optional[str] = None
    ) -> MentalHealthAssessment:
        """Criar nova avaliação clínica"""
        assessment = MentalHealthAssessment(
            patient_id=patient_id,
            scale_type=scale_type,
            score=score,
            severity_level=severity_level,
            questions_answers=questions_answers,
            professional_id=professional_id,
            notes=notes,
            interpretation=interpretation
        )
        session.add(assessment)
        await session.commit()
        await session.refresh(assessment)
        logger.info(f"Avaliação {scale_type} criada para paciente {patient_id} - Score: {score}")
        return assessment

    @staticmethod
    async def get_latest_assessment_by_type(
        session: AsyncSession,
        patient_id: int,
        scale_type: str
    ) -> Optional[MentalHealthAssessment]:
        """Buscar última avaliação de um tipo específico"""
        result = await session.execute(
            select(MentalHealthAssessment)
            .where(
                and_(
                    MentalHealthAssessment.patient_id == patient_id,
                    MentalHealthAssessment.scale_type == scale_type
                )
            )
            .order_by(desc(MentalHealthAssessment.assessed_at))
            .limit(1)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_assessment_history(
        session: AsyncSession,
        patient_id: int,
        scale_type: Optional[str] = None,
        days: int = 90
    ) -> List[MentalHealthAssessment]:
        """Buscar histórico de avaliações"""
        start_date = datetime.now() - timedelta(days=days)

        query = select(MentalHealthAssessment).where(
            and_(
                MentalHealthAssessment.patient_id == patient_id,
                MentalHealthAssessment.assessed_at >= start_date
            )
        )

        if scale_type:
            query = query.where(MentalHealthAssessment.scale_type == scale_type)

        query = query.order_by(desc(MentalHealthAssessment.assessed_at))

        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_assessment_trend(
        session: AsyncSession,
        patient_id: int,
        scale_type: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Calcular tendência de scores (melhorando/piorando/estável)"""
        assessments = await MentalHealthRepository.get_assessment_history(
            session, patient_id, scale_type, days=180
        )

        if len(assessments) < 2:
            return {"trend": "insufficient_data", "assessments": assessments}

        scores = [a.score for a in assessments[:limit]]
        scores.reverse()  # Ordem cronológica

        # Calcular tendência simples (comparar média primeira metade vs segunda metade)
        mid = len(scores) // 2
        first_half_avg = sum(scores[:mid]) / mid if mid > 0 else 0
        second_half_avg = sum(scores[mid:]) / (len(scores) - mid) if len(scores) > mid else 0

        diff = second_half_avg - first_half_avg

        if abs(diff) < 2:  # Diferença < 2 pontos = estável
            trend = "stable"
        elif diff > 0:
            trend = "worsening"  # Score maior = pior (para PHQ-9, GAD-7, etc)
        else:
            trend = "improving"

        return {
            "trend": trend,
            "diff": round(diff, 2),
            "first_half_avg": round(first_half_avg, 2),
            "second_half_avg": round(second_half_avg, 2),
            "assessments": assessments[:limit]
        }

    # ===============================================================
    # MOOD DIARY (Diário de Humor)
    # ===============================================================

    @staticmethod
    async def create_mood_entry(
        session: AsyncSession,
        patient_id: int,
        date: date,
        time_of_day: str,
        mood_score: Optional[int] = None,
        anxiety_level: Optional[int] = None,
        energy_level: Optional[int] = None,
        sleep_quality: Optional[int] = None,
        sleep_hours: Optional[float] = None,
        awakenings: Optional[int] = None,
        notes: Optional[str] = None,
        symptoms: List[str] = [],
        triggers: List[str] = [],
        helpful_activities: List[str] = [],
        physical_symptoms: List[str] = [],
        intrusive_thoughts: bool = False,
        intrusive_thoughts_description: Optional[str] = None,
        accomplished_planned_activities: Optional[bool] = None
    ) -> MoodDiary:
        """Criar entrada no diário de humor"""
        mood_entry = MoodDiary(
            patient_id=patient_id,
            date=date,
            time_of_day=time_of_day,
            mood_score=mood_score,
            anxiety_level=anxiety_level,
            energy_level=energy_level,
            sleep_quality=sleep_quality,
            sleep_hours=sleep_hours,
            awakenings=awakenings,
            notes=notes,
            symptoms=symptoms,
            triggers=triggers,
            helpful_activities=helpful_activities,
            physical_symptoms=physical_symptoms,
            intrusive_thoughts=intrusive_thoughts,
            intrusive_thoughts_description=intrusive_thoughts_description,
            accomplished_planned_activities=accomplished_planned_activities
        )
        session.add(mood_entry)
        await session.commit()
        await session.refresh(mood_entry)
        logger.info(f"Entrada de humor criada para paciente {patient_id} - {date} {time_of_day}")
        return mood_entry

    @staticmethod
    async def get_mood_history(
        session: AsyncSession,
        patient_id: int,
        days: int = 30
    ) -> List[MoodDiary]:
        """Buscar histórico de humor"""
        start_date = date.today() - timedelta(days=days)

        result = await session.execute(
            select(MoodDiary)
            .where(
                and_(
                    MoodDiary.patient_id == patient_id,
                    MoodDiary.date >= start_date
                )
            )
            .order_by(desc(MoodDiary.date), MoodDiary.time_of_day)
        )
        return result.scalars().all()

    @staticmethod
    async def get_mood_statistics(
        session: AsyncSession,
        patient_id: int,
        days: int = 7
    ) -> Dict[str, Any]:
        """Calcular estatísticas de humor"""
        entries = await MentalHealthRepository.get_mood_history(session, patient_id, days)

        if not entries:
            return {"error": "no_data"}

        mood_scores = [e.mood_score for e in entries if e.mood_score is not None]
        anxiety_levels = [e.anxiety_level for e in entries if e.anxiety_level is not None]
        energy_levels = [e.energy_level for e in entries if e.energy_level is not None]

        return {
            "avg_mood": round(sum(mood_scores) / len(mood_scores), 2) if mood_scores else None,
            "avg_anxiety": round(sum(anxiety_levels) / len(anxiety_levels), 2) if anxiety_levels else None,
            "avg_energy": round(sum(energy_levels) / len(energy_levels), 2) if energy_levels else None,
            "entries_count": len(entries),
            "days_analyzed": days
        }

    # ===============================================================
    # CRISIS EVENTS
    # ===============================================================

    @staticmethod
    async def create_crisis_event(
        session: AsyncSession,
        patient_id: int,
        crisis_type: str,
        severity: str,
        occurred_at: datetime,
        **kwargs
    ) -> CrisisEvent:
        """Registrar evento de crise"""
        crisis = CrisisEvent(
            patient_id=patient_id,
            crisis_type=crisis_type,
            severity=severity,
            occurred_at=occurred_at,
            **kwargs
        )
        session.add(crisis)
        await session.commit()
        await session.refresh(crisis)
        logger.warning(f"🚨 CRISE REGISTRADA: {crisis_type} - Paciente {patient_id} - Severidade: {severity}")
        return crisis

    @staticmethod
    async def get_recent_crises(
        session: AsyncSession,
        patient_id: int,
        days: int = 30
    ) -> List[CrisisEvent]:
        """Buscar crises recentes"""
        start_date = datetime.now() - timedelta(days=days)

        result = await session.execute(
            select(CrisisEvent)
            .where(
                and_(
                    CrisisEvent.patient_id == patient_id,
                    CrisisEvent.occurred_at >= start_date
                )
            )
            .order_by(desc(CrisisEvent.occurred_at))
        )
        return result.scalars().all()

    # ===============================================================
    # SAFETY PLANS
    # ===============================================================

    @staticmethod
    async def get_active_safety_plan(
        session: AsyncSession,
        patient_id: int
    ) -> Optional[SafetyPlan]:
        """Buscar plano de segurança ativo"""
        result = await session.execute(
            select(SafetyPlan)
            .where(
                and_(
                    SafetyPlan.patient_id == patient_id,
                    SafetyPlan.active == True
                )
            )
            .order_by(desc(SafetyPlan.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_safety_plan(
        session: AsyncSession,
        patient_id: int,
        created_by: int,
        warning_signs: List[str],
        internal_coping_strategies: List[str],
        people_to_contact: List[Dict],
        professionals_to_contact: List[Dict],
        crisis_hotlines: List[Dict],
        **kwargs
    ) -> SafetyPlan:
        """Criar plano de segurança"""
        # Desativar planos anteriores
        await session.execute(
            select(SafetyPlan)
            .where(
                and_(
                    SafetyPlan.patient_id == patient_id,
                    SafetyPlan.active == True
                )
            )
        )

        # Criar novo plano
        safety_plan = SafetyPlan(
            patient_id=patient_id,
            created_by=created_by,
            warning_signs=warning_signs,
            internal_coping_strategies=internal_coping_strategies,
            people_to_contact=people_to_contact,
            professionals_to_contact=professionals_to_contact,
            crisis_hotlines=crisis_hotlines,
            **kwargs
        )
        session.add(safety_plan)
        await session.commit()
        await session.refresh(safety_plan)
        logger.info(f"Plano de segurança criado para paciente {patient_id}")
        return safety_plan

    # ===============================================================
    # NLP CONVERSATION ANALYSIS
    # ===============================================================

    @staticmethod
    async def create_nlp_analysis(
        session: AsyncSession,
        patient_id: int,
        sentiment_score: float,
        sentiment_label: str,
        detected_keywords: List[str],
        danger_flags: List[str],
        **kwargs
    ) -> NLPConversationAnalysis:
        """Criar análise NLP de conversa"""
        analysis = NLPConversationAnalysis(
            patient_id=patient_id,
            sentiment_score=sentiment_score,
            sentiment_label=sentiment_label,
            detected_keywords=detected_keywords,
            danger_flags=danger_flags,
            **kwargs
        )
        session.add(analysis)
        await session.commit()
        await session.refresh(analysis)

        if danger_flags:
            logger.warning(f"⚠️ Flags de perigo detectados: {danger_flags} - Paciente {patient_id}")

        return analysis

    @staticmethod
    async def get_recent_sentiment_trend(
        session: AsyncSession,
        patient_id: int,
        days: int = 7
    ) -> Dict[str, Any]:
        """Calcular tendência de sentimento nas conversas"""
        start_date = datetime.now() - timedelta(days=days)

        result = await session.execute(
            select(NLPConversationAnalysis)
            .where(
                and_(
                    NLPConversationAnalysis.patient_id == patient_id,
                    NLPConversationAnalysis.analyzed_at >= start_date
                )
            )
            .order_by(NLPConversationAnalysis.analyzed_at)
        )
        analyses = result.scalars().all()

        if not analyses:
            return {"error": "no_data"}

        scores = [a.sentiment_score for a in analyses if a.sentiment_score is not None]
        avg_sentiment = sum(scores) / len(scores) if scores else 0

        # Contar flags de perigo
        danger_flags_count = {}
        for analysis in analyses:
            if analysis.danger_flags:
                for flag in analysis.danger_flags:
                    danger_flags_count[flag] = danger_flags_count.get(flag, 0) + 1

        return {
            "avg_sentiment": round(avg_sentiment, 4),
            "analyses_count": len(analyses),
            "danger_flags_count": danger_flags_count,
            "trend": "negative" if avg_sentiment < -0.2 else ("positive" if avg_sentiment > 0.2 else "neutral")
        }

    # ===============================================================
    # ML PREDICTIONS
    # ===============================================================

    @staticmethod
    async def create_ml_prediction(
        session: AsyncSession,
        patient_id: int,
        model_name: str,
        prediction_type: str,
        prediction_value: float,
        prediction_label: str,
        confidence_score: float,
        features_used: Dict,
        valid_until: datetime
    ) -> MLPrediction:
        """Criar predição de ML"""
        prediction = MLPrediction(
            patient_id=patient_id,
            model_name=model_name,
            prediction_type=prediction_type,
            prediction_value=prediction_value,
            prediction_label=prediction_label,
            confidence_score=confidence_score,
            features_used=features_used,
            valid_until=valid_until
        )
        session.add(prediction)
        await session.commit()
        await session.refresh(prediction)

        if prediction_type == "suicide_risk" and prediction_label in ["HIGH", "CRITICAL"]:
            logger.critical(f"🚨 ALERTA ML: Risco de suicídio {prediction_label} - Paciente {patient_id}")

        return prediction

    @staticmethod
    async def get_latest_prediction(
        session: AsyncSession,
        patient_id: int,
        prediction_type: str
    ) -> Optional[MLPrediction]:
        """Buscar última predição válida"""
        result = await session.execute(
            select(MLPrediction)
            .where(
                and_(
                    MLPrediction.patient_id == patient_id,
                    MLPrediction.prediction_type == prediction_type,
                    MLPrediction.valid_until >= datetime.now()
                )
            )
            .order_by(desc(MLPrediction.predicted_at))
            .limit(1)
        )
        return result.scalar_one_or_none()

    # ===============================================================
    # ASSESSMENT SCALES REFERENCE
    # ===============================================================

    @staticmethod
    async def get_scale_reference(
        session: AsyncSession,
        scale_type: str,
        language: str = 'pt-BR'
    ) -> Optional[AssessmentScaleReference]:
        """Buscar questões de uma escala de avaliação"""
        result = await session.execute(
            select(AssessmentScaleReference)
            .where(
                and_(
                    AssessmentScaleReference.scale_type == scale_type,
                    AssessmentScaleReference.language == language
                )
            )
            .order_by(desc(AssessmentScaleReference.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()

    # ===============================================================
    # MENTAL HEALTH SUMMARY
    # ===============================================================

    @staticmethod
    async def get_patient_mental_health_summary(
        session: AsyncSession,
        patient_id: int
    ) -> Dict[str, Any]:
        """Obter resumo completo de saúde mental do paciente"""

        # PHQ-9 (Depressão)
        latest_phq9 = await MentalHealthRepository.get_latest_assessment_by_type(
            session, patient_id, 'PHQ9'
        )

        # GAD-7 (Ansiedade)
        latest_gad7 = await MentalHealthRepository.get_latest_assessment_by_type(
            session, patient_id, 'GAD7'
        )

        # C-SSRS (Risco Suicida)
        latest_cssrs = await MentalHealthRepository.get_latest_assessment_by_type(
            session, patient_id, 'C-SSRS'
        )

        # Humor (7 dias)
        mood_stats = await MentalHealthRepository.get_mood_statistics(session, patient_id, days=7)

        # Crises (30 dias)
        recent_crises = await MentalHealthRepository.get_recent_crises(session, patient_id, days=30)

        # Sentimento (7 dias)
        sentiment_trend = await MentalHealthRepository.get_recent_sentiment_trend(session, patient_id, days=7)

        # Plano de segurança
        safety_plan = await MentalHealthRepository.get_active_safety_plan(session, patient_id)

        return {
            "patient_id": patient_id,
            "assessments": {
                "phq9": {
                    "score": latest_phq9.score if latest_phq9 else None,
                    "severity": latest_phq9.severity_level if latest_phq9 else None,
                    "date": latest_phq9.assessed_at if latest_phq9 else None
                },
                "gad7": {
                    "score": latest_gad7.score if latest_gad7 else None,
                    "severity": latest_gad7.severity_level if latest_gad7 else None,
                    "date": latest_gad7.assessed_at if latest_gad7 else None
                },
                "cssrs": {
                    "score": latest_cssrs.score if latest_cssrs else None,
                    "risk": latest_cssrs.interpretation if latest_cssrs else None,
                    "date": latest_cssrs.assessed_at if latest_cssrs else None
                }
            },
            "mood_stats_7d": mood_stats,
            "sentiment_trend_7d": sentiment_trend,
            "crisis_count_30d": len(recent_crises),
            "has_active_safety_plan": safety_plan is not None,
            "risk_level": MentalHealthRepository._calculate_overall_risk(
                latest_phq9, latest_gad7, latest_cssrs, recent_crises
            )
        }

    @staticmethod
    def _calculate_overall_risk(
        phq9: Optional[MentalHealthAssessment],
        gad7: Optional[MentalHealthAssessment],
        cssrs: Optional[MentalHealthAssessment],
        recent_crises: List[CrisisEvent]
    ) -> str:
        """Calcular nível de risco geral"""

        # Risco crítico
        if cssrs and cssrs.score >= 4:
            return "CRITICAL"
        if len(recent_crises) > 0 and any(c.crisis_type == 'suicide_attempt' for c in recent_crises):
            return "CRITICAL"

        # Risco alto
        if cssrs and cssrs.score >= 2:
            return "HIGH"
        if phq9 and phq9.score >= 20:
            return "HIGH"
        if gad7 and gad7.score >= 15:
            return "HIGH"

        # Risco moderado
        if phq9 and phq9.score >= 10:
            return "MODERATE"
        if gad7 and gad7.score >= 10:
            return "MODERATE"

        # Risco baixo
        return "LOW"
