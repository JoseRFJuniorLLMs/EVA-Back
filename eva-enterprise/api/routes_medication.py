"""
Rotas FastAPI para Gestão de Medicação (Saúde Mental)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from datetime import datetime, date, timedelta
import logging

from database.connection import get_db
from database.models import (
    # Medication, MedicationSchedule, MedicationLog,  # TODO: Create these models
    MedicationSideEffect, Idoso
)
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/mental-health/medication", tags=["Dashboard - Saude Mental"])
logger = logging.getLogger(__name__)


# =====================================================================
# SCHEMAS
# =====================================================================

class MedicationCreate(BaseModel):
    patient_id: int
    name: str
    dosage: str
    purpose: str = Field(..., description="ansiolítico, antidepressivo, estabilizador, etc")
    start_date: date
    end_date: date | None = None
    prescribing_doctor: str | None = None
    notes: str | None = None


class ScheduleCreate(BaseModel):
    medication_id: int
    time_of_day: str = Field(..., description="morning, afternoon, evening, night")
    hour: str = Field(..., description="HH:MM")
    days_of_week: List[int] = Field(default=[0,1,2,3,4,5,6], description="0=domingo, 6=sábado")


class MedicationLogCreate(BaseModel):
    medication_id: int
    scheduled_time: datetime
    taken_at: datetime | None = None
    taken: bool = False
    skipped_reason: str | None = None


class SideEffectCreate(BaseModel):
    patient_id: int
    medication_id: int
    side_effect: str
    severity: str = Field(..., description="mild, moderate, severe")
    reported_at: datetime = Field(default_factory=datetime.now)
    notes: str | None = None


# =====================================================================
# ENDPOINTS - MEDICAMENTOS
# =====================================================================

@router.post("/medications", status_code=status.HTTP_201_CREATED)
async def create_medication(
    data: MedicationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Cadastrar novo medicamento"""
    from ..database.models import Medication

    med = Medication(
        patient_id=data.patient_id,
        name=data.name,
        dosage=data.dosage,
        purpose=data.purpose,
        start_date=data.start_date,
        end_date=data.end_date,
        prescribing_doctor=data.prescribing_doctor,
        notes=data.notes,
        active=True
    )

    db.add(med)
    await db.commit()
    await db.refresh(med)

    return {
        "id": med.id,
        "name": med.name,
        "dosage": med.dosage,
        "purpose": med.purpose,
        "active": med.active
    }


@router.get("/medications/{patient_id}")
async def get_patient_medications(
    patient_id: int,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Listar medicamentos do paciente"""
    from ..database.models import Medication

    query = select(Medication).where(Medication.patient_id == patient_id)

    if active_only:
        query = query.where(Medication.active == True)

    query = query.order_by(Medication.created_at.desc())

    result = await db.execute(query)
    medications = result.scalars().all()

    return [
        {
            "id": med.id,
            "name": med.name,
            "dosage": med.dosage,
            "purpose": med.purpose,
            "start_date": med.start_date.isoformat() if med.start_date else None,
            "end_date": med.end_date.isoformat() if med.end_date else None,
            "active": med.active,
            "prescribing_doctor": med.prescribing_doctor
        }
        for med in medications
    ]


@router.post("/schedules", status_code=status.HTTP_201_CREATED)
async def create_schedule(
    data: ScheduleCreate,
    db: AsyncSession = Depends(get_db)
):
    """Criar horário de medicamento"""
    from ..database.models import MedicationSchedule

    schedule = MedicationSchedule(
        medication_id=data.medication_id,
        time_of_day=data.time_of_day,
        hour=data.hour,
        days_of_week=data.days_of_week,
        active=True
    )

    db.add(schedule)
    await db.commit()
    await db.refresh(schedule)

    return {
        "id": schedule.id,
        "medication_id": schedule.medication_id,
        "time_of_day": schedule.time_of_day,
        "hour": schedule.hour,
        "days_of_week": schedule.days_of_week
    }


@router.get("/schedules/{medication_id}")
async def get_medication_schedules(
    medication_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Buscar horários de um medicamento"""
    from ..database.models import MedicationSchedule

    query = select(MedicationSchedule).where(
        and_(
            MedicationSchedule.medication_id == medication_id,
            MedicationSchedule.active == True
        )
    ).order_by(MedicationSchedule.hour)

    result = await db.execute(query)
    schedules = result.scalars().all()

    return [
        {
            "id": s.id,
            "time_of_day": s.time_of_day,
            "hour": s.hour,
            "days_of_week": s.days_of_week
        }
        for s in schedules
    ]


# =====================================================================
# ENDPOINTS - REGISTRO DE TOMADAS
# =====================================================================

@router.post("/logs", status_code=status.HTTP_201_CREATED)
async def log_medication_taken(
    data: MedicationLogCreate,
    db: AsyncSession = Depends(get_db)
):
    """Registrar tomada de medicamento"""
    from ..database.models import MedicationLog

    log = MedicationLog(
        medication_id=data.medication_id,
        scheduled_time=data.scheduled_time,
        taken_at=data.taken_at or datetime.now(),
        taken=data.taken,
        skipped_reason=data.skipped_reason
    )

    db.add(log)
    await db.commit()
    await db.refresh(log)

    return {
        "id": log.id,
        "medication_id": log.medication_id,
        "taken": log.taken,
        "taken_at": log.taken_at.isoformat() if log.taken_at else None
    }


@router.get("/logs/{patient_id}/history")
async def get_medication_history(
    patient_id: int,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Histórico de tomadas"""
    from ..database.models import MedicationLog, Medication

    start_date = datetime.now() - timedelta(days=days)

    query = select(MedicationLog, Medication).join(
        Medication, MedicationLog.medication_id == Medication.id
    ).where(
        and_(
            Medication.patient_id == patient_id,
            MedicationLog.scheduled_time >= start_date
        )
    ).order_by(MedicationLog.scheduled_time.desc())

    result = await db.execute(query)
    logs = result.all()

    return [
        {
            "id": log.MedicationLog.id,
            "medication_name": log.Medication.name,
            "medication_id": log.MedicationLog.medication_id,
            "scheduled_time": log.MedicationLog.scheduled_time.isoformat(),
            "taken_at": log.MedicationLog.taken_at.isoformat() if log.MedicationLog.taken_at else None,
            "taken": log.MedicationLog.taken,
            "skipped_reason": log.MedicationLog.skipped_reason
        }
        for log in logs
    ]


@router.get("/logs/{patient_id}/adherence")
async def get_medication_adherence(
    patient_id: int,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Calcular taxa de adesão"""
    from ..database.models import MedicationLog, Medication
    from sqlalchemy import func

    start_date = datetime.now() - timedelta(days=days)

    # Total programado
    query_total = select(func.count(MedicationLog.id)).join(
        Medication, MedicationLog.medication_id == Medication.id
    ).where(
        and_(
            Medication.patient_id == patient_id,
            MedicationLog.scheduled_time >= start_date
        )
    )

    result = await db.execute(query_total)
    total = result.scalar() or 0

    # Total tomado
    query_taken = select(func.count(MedicationLog.id)).join(
        Medication, MedicationLog.medication_id == Medication.id
    ).where(
        and_(
            Medication.patient_id == patient_id,
            MedicationLog.scheduled_time >= start_date,
            MedicationLog.taken == True
        )
    )

    result = await db.execute(query_taken)
    taken = result.scalar() or 0

    adherence_rate = (taken / total * 100) if total > 0 else 0

    return {
        "patient_id": patient_id,
        "period_days": days,
        "total_scheduled": total,
        "total_taken": taken,
        "total_skipped": total - taken,
        "adherence_rate": round(adherence_rate, 2)
    }


# =====================================================================
# ENDPOINTS - EFEITOS COLATERAIS
# =====================================================================

@router.post("/side-effects", status_code=status.HTTP_201_CREATED)
async def report_side_effect(
    data: SideEffectCreate,
    db: AsyncSession = Depends(get_db)
):
    """Reportar efeito colateral"""
    from ..database.models import MedicationSideEffect

    effect = MedicationSideEffect(
        patient_id=data.patient_id,
        medication_id=data.medication_id,
        side_effect=data.side_effect,
        severity=data.severity,
        reported_at=data.reported_at,
        notes=data.notes
    )

    db.add(effect)
    await db.commit()
    await db.refresh(effect)

    return {
        "id": effect.id,
        "side_effect": effect.side_effect,
        "severity": effect.severity,
        "reported_at": effect.reported_at.isoformat()
    }


@router.get("/side-effects/{medication_id}")
async def get_medication_side_effects(
    medication_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Listar efeitos colaterais de um medicamento"""
    from ..database.models import MedicationSideEffect

    query = select(MedicationSideEffect).where(
        MedicationSideEffect.medication_id == medication_id
    ).order_by(MedicationSideEffect.reported_at.desc())

    result = await db.execute(query)
    effects = result.scalars().all()

    return [
        {
            "id": e.id,
            "side_effect": e.side_effect,
            "severity": e.severity,
            "reported_at": e.reported_at.isoformat(),
            "notes": e.notes
        }
        for e in effects
    ]


# =====================================================================
# ENDPOINT - CORRELAÇÕES
# =====================================================================

@router.get("/correlations/{patient_id}")
async def get_medication_correlations(
    patient_id: int,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Correlações: medicação x humor/sono/ansiedade"""
    from ..database.models import MedicationLog, Medication, MoodDiary
    from sqlalchemy import func, case

    start_date = datetime.now() - timedelta(days=days)

    # Pegar logs de medicação
    query_logs = select(
        func.date(MedicationLog.taken_at).label('date'),
        func.count(case((MedicationLog.taken == True, 1))).label('taken_count')
    ).join(
        Medication, MedicationLog.medication_id == Medication.id
    ).where(
        and_(
            Medication.patient_id == patient_id,
            MedicationLog.taken_at >= start_date
        )
    ).group_by(func.date(MedicationLog.taken_at))

    result_logs = await db.execute(query_logs)
    med_data = {row.date: row.taken_count for row in result_logs}

    # Pegar dados de humor
    query_mood = select(
        MoodDiary.date,
        func.avg(MoodDiary.mood_score).label('avg_mood'),
        func.avg(MoodDiary.anxiety_level).label('avg_anxiety'),
        func.avg(MoodDiary.sleep_quality).label('avg_sleep')
    ).where(
        and_(
            MoodDiary.patient_id == patient_id,
            MoodDiary.date >= start_date.date()
        )
    ).group_by(MoodDiary.date)

    result_mood = await db.execute(query_mood)
    mood_data = {row.date: row for row in result_mood}

    # Combinar dados
    correlation_data = []
    for dt, taken_count in med_data.items():
        if dt in mood_data:
            mood_row = mood_data[dt]
            correlation_data.append({
                "date": dt.isoformat(),
                "medications_taken": taken_count,
                "avg_mood": float(mood_row.avg_mood) if mood_row.avg_mood else None,
                "avg_anxiety": float(mood_row.avg_anxiety) if mood_row.avg_anxiety else None,
                "avg_sleep": float(mood_row.avg_sleep) if mood_row.avg_sleep else None
            })

    return correlation_data
