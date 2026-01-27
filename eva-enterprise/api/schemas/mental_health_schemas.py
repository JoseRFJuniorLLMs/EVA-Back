"""
Schemas Pydantic para validação de dados de saúde mental
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum


# =====================================================================
# ENUMS
# =====================================================================

class ScaleType(str, Enum):
    """Tipos de escalas de avaliação clínica"""
    PHQ9 = "PHQ9"
    GAD7 = "GAD7"
    C_SSRS = "C-SSRS"
    PSS10 = "PSS10"
    Y_BOCS = "Y-BOCS"
    PCL5 = "PCL5"
    BDI = "BDI"
    BAI = "BAI"


class SeverityLevel(str, Enum):
    """Níveis de severidade"""
    MINIMAL = "minimal"
    MILD = "mild"
    MODERATE = "moderate"
    MODERATELY_SEVERE = "moderately_severe"
    SEVERE = "severe"
    EXTREMELY_SEVERE = "extremely_severe"


class TimeOfDay(str, Enum):
    """Períodos do dia"""
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"


class RiskLevel(str, Enum):
    """Níveis de risco"""
    NONE = "NONE"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CrisisType(str, Enum):
    """Tipos de crise"""
    SUICIDAL_IDEATION = "suicidal_ideation"
    SUICIDE_ATTEMPT = "suicide_attempt"
    SELF_HARM = "self_harm"
    PANIC_ATTACK = "panic_attack"
    PSYCHOTIC_EPISODE = "psychotic_episode"
    SEVERE_DEPRESSION = "severe_depression"
    SEVERE_ANXIETY = "severe_anxiety"
    OTHER = "other"


# =====================================================================
# ASSESSMENT SCHEMAS
# =====================================================================

class QuestionAnswer(BaseModel):
    """Pergunta e resposta de uma avaliação"""
    question_id: int
    question_text: str
    answer: int
    score: int


class AssessmentCreate(BaseModel):
    """Criar nova avaliação"""
    patient_id: int = Field(..., gt=0)
    scale_type: ScaleType
    questions_answers: List[QuestionAnswer]
    professional_id: Optional[int] = None
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": 123,
                "scale_type": "PHQ9",
                "questions_answers": [
                    {
                        "question_id": 1,
                        "question_text": "Pouco interesse ou prazer em fazer as coisas",
                        "answer": 2,
                        "score": 2
                    }
                ],
                "notes": "Paciente relatou melhora desde última avaliação"
            }
        }


class AssessmentResponse(BaseModel):
    """Resposta de avaliação"""
    id: int
    patient_id: int
    scale_type: str
    score: int
    severity_level: str
    assessed_at: datetime
    questions_answers: List[Dict]
    professional_id: Optional[int]
    notes: Optional[str]
    interpretation: Optional[str]

    class Config:
        from_attributes = True


class AssessmentTrend(BaseModel):
    """Tendência de avaliações"""
    trend: str  # improving, worsening, stable, insufficient_data
    diff: Optional[float]
    first_half_avg: Optional[float]
    second_half_avg: Optional[float]
    assessments: List[AssessmentResponse]


# =====================================================================
# MOOD DIARY SCHEMAS
# =====================================================================

class MoodDiaryCreate(BaseModel):
    """Criar entrada no diário de humor"""
    patient_id: int = Field(..., gt=0)
    entry_date: date = Field(default_factory=date.today)
    time_of_day: TimeOfDay
    mood_score: Optional[int] = Field(None, ge=1, le=10)
    anxiety_level: Optional[int] = Field(None, ge=1, le=10)
    energy_level: Optional[int] = Field(None, ge=1, le=10)
    sleep_quality: Optional[int] = Field(None, ge=1, le=10)
    sleep_hours: Optional[float] = Field(None, ge=0, le=24)
    awakenings: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None
    symptoms: List[str] = Field(default_factory=list)
    triggers: List[str] = Field(default_factory=list)
    helpful_activities: List[str] = Field(default_factory=list)
    physical_symptoms: List[str] = Field(default_factory=list)
    intrusive_thoughts: bool = False
    intrusive_thoughts_description: Optional[str] = None
    accomplished_planned_activities: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": 123,
                "entry_date": "2026-01-24",
                "time_of_day": "evening",
                "mood_score": 6,
                "anxiety_level": 4,
                "energy_level": 5,
                "sleep_quality": 7,
                "sleep_hours": 7.5,
                "awakenings": 1,
                "symptoms": ["headache", "muscle_tension"],
                "triggers": ["work_stress"],
                "helpful_activities": ["meditation", "exercise"]
            }
        }


class MoodDiaryResponse(BaseModel):
    """Resposta de entrada no diário"""
    id: int
    patient_id: int
    entry_date: date
    time_of_day: str
    mood_score: Optional[int]
    anxiety_level: Optional[int]
    energy_level: Optional[int]
    sleep_quality: Optional[int]
    sleep_hours: Optional[float]
    awakenings: Optional[int]
    notes: Optional[str]
    symptoms: List[str]
    triggers: List[str]
    helpful_activities: List[str]
    intrusive_thoughts: bool
    created_at: datetime

    class Config:
        from_attributes = True


class MoodStatistics(BaseModel):
    """Estatísticas de humor"""
    avg_mood: Optional[float]
    avg_anxiety: Optional[float]
    avg_energy: Optional[float]
    entries_count: int
    days_analyzed: int


# =====================================================================
# CRISIS EVENT SCHEMAS
# =====================================================================

class CrisisEventCreate(BaseModel):
    """Registrar evento de crise"""
    patient_id: int = Field(..., gt=0)
    crisis_type: CrisisType
    severity: SeverityLevel
    occurred_at: datetime
    duration_minutes: Optional[int] = None
    location: Optional[str] = None
    precipitating_factors: List[str] = Field(default_factory=list)
    warning_signs: List[str] = Field(default_factory=list)
    intervention_taken: List[str] = Field(default_factory=list)
    emergency_contacts_notified: List[Dict] = Field(default_factory=list)
    hospitalization_required: bool = False
    hospital_name: Optional[str] = None
    notes: Optional[str] = None


class CrisisEventResponse(BaseModel):
    """Resposta de evento de crise"""
    id: int
    patient_id: int
    crisis_type: str
    severity: str
    occurred_at: datetime
    duration_minutes: Optional[int]
    location: Optional[str]
    precipitating_factors: List[str]
    warning_signs: List[str]
    intervention_taken: List[str]
    hospitalization_required: bool
    created_at: datetime

    class Config:
        from_attributes = True


# =====================================================================
# SAFETY PLAN SCHEMAS
# =====================================================================

class ContactPerson(BaseModel):
    """Pessoa de contato"""
    name: str
    phone: str
    relationship: str


class CrisisHotline(BaseModel):
    """Linha de crise"""
    name: str
    phone: str
    available: str = "24/7"


class SafetyPlanCreate(BaseModel):
    """Criar plano de segurança"""
    patient_id: int = Field(..., gt=0)
    created_by: int = Field(..., gt=0)
    warning_signs: List[str]
    internal_coping_strategies: List[str]
    social_distractions: List[str] = Field(default_factory=list)
    people_to_contact: List[ContactPerson]
    professionals_to_contact: List[ContactPerson]
    crisis_hotlines: List[CrisisHotline]
    environment_safety: List[str] = Field(default_factory=list)
    reasons_for_living: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": 123,
                "created_by": 456,
                "warning_signs": ["Feeling hopeless", "Social withdrawal"],
                "internal_coping_strategies": ["Deep breathing", "Journaling"],
                "people_to_contact": [
                    {"name": "Maria Silva", "phone": "11999999999", "relationship": "Filha"}
                ],
                "professionals_to_contact": [
                    {"name": "Dr. João", "phone": "1133333333", "relationship": "Psiquiatra"}
                ],
                "crisis_hotlines": [
                    {"name": "CVV", "phone": "188", "available": "24/7"}
                ],
                "reasons_for_living": ["Meus netos", "Viajar para praia"]
            }
        }


class SafetyPlanResponse(BaseModel):
    """Resposta de plano de segurança"""
    id: int
    patient_id: int
    created_by: int
    warning_signs: List[str]
    internal_coping_strategies: List[str]
    people_to_contact: List[Dict]
    professionals_to_contact: List[Dict]
    crisis_hotlines: List[Dict]
    reasons_for_living: List[str]
    active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =====================================================================
# NLP ANALYSIS SCHEMAS
# =====================================================================

class NLPAnalysisCreate(BaseModel):
    """Criar análise NLP"""
    patient_id: int = Field(..., gt=0)
    conversation_session_id: Optional[int] = None
    message_id: Optional[int] = None
    sentiment_score: float = Field(..., ge=-1, le=1)
    sentiment_label: str
    detected_keywords: List[str] = Field(default_factory=list)
    danger_flags: List[str] = Field(default_factory=list)
    extracted_entities: Dict[str, List[str]] = Field(default_factory=dict)
    topic_classification: List[str] = Field(default_factory=list)


class SentimentTrend(BaseModel):
    """Tendência de sentimento"""
    avg_sentiment: float
    analyses_count: int
    danger_flags_count: Dict[str, int]
    trend: str  # negative, neutral, positive


# =====================================================================
# ML PREDICTION SCHEMAS
# =====================================================================

class MLPredictionCreate(BaseModel):
    """Criar predição de ML"""
    patient_id: int = Field(..., gt=0)
    model_name: str
    model_version: Optional[str] = None
    prediction_type: str
    prediction_value: float = Field(..., ge=0, le=1)
    prediction_label: str
    confidence_score: float = Field(..., ge=0, le=1)
    features_used: Dict[str, Any]
    valid_until: datetime


class MLPredictionResponse(BaseModel):
    """Resposta de predição"""
    id: int
    patient_id: int
    model_name: str
    prediction_type: str
    prediction_value: float
    prediction_label: str
    confidence_score: float
    predicted_at: datetime
    valid_until: datetime

    class Config:
        from_attributes = True


# =====================================================================
# PATIENT SUMMARY SCHEMA
# =====================================================================

class AssessmentSummary(BaseModel):
    """Resumo de avaliação"""
    score: Optional[int]
    severity: Optional[str]
    date: Optional[datetime]


class PatientMentalHealthSummary(BaseModel):
    """Resumo completo de saúde mental"""
    patient_id: int
    assessments: Dict[str, AssessmentSummary]
    mood_stats_7d: Dict[str, Any]
    sentiment_trend_7d: Dict[str, Any]
    crisis_count_30d: int
    has_active_safety_plan: bool
    risk_level: RiskLevel


# =====================================================================
# SCALE REFERENCE SCHEMAS
# =====================================================================

class ScaleQuestion(BaseModel):
    """Questão de escala"""
    id: int
    text: str
    options: List[str]
    scores: List[int]


class ScaleReference(BaseModel):
    """Referência de escala de avaliação"""
    scale_type: str
    version: str
    language: str
    questions: List[ScaleQuestion]
    scoring_rules: Dict[str, Any]
    interpretation_guide: List[Dict[str, Any]]


# =====================================================================
# EMERGENCY PROTOCOL SCHEMAS
# =====================================================================

class EmergencyAlert(BaseModel):
    """Alerta de emergência"""
    patient_id: int
    risk_level: RiskLevel
    trigger_reason: str
    detected_at: datetime
    actions_taken: List[str]
    safety_plan_activated: bool
    contacts_notified: List[Dict]


class EmergencyProtocolActivation(BaseModel):
    """Ativação de protocolo de emergência"""
    patient_id: int = Field(..., gt=0)
    trigger_type: str  # c_ssrs_high, ml_prediction, keyword_detection
    trigger_details: Dict[str, Any]
    immediate_actions: List[str]
    notify_contacts: bool = True
    activate_safety_plan: bool = True
