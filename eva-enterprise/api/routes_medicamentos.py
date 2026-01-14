from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db
from database.repositories.medicamento_repo import MedicamentoRepository, SinaisVitaisRepository
from schemas import (
    MedicamentoCreate, MedicamentoResponse,
    SinaisVitaisCreate, SinaisVitaisResponse,
    MessageResponse
)
from services.clinical_service import ClinicalService
from typing import Optional, Dict, Any
from typing import List
from utils.security import get_current_user, check_role
from database.repositories.alerta_repo import AlertaRepository

router = APIRouter()

# --- Medicamentos ---

@router.get("/", response_model=List[MedicamentoResponse])
async def list_todos_medicamentos(db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    repo = MedicamentoRepository(db)
    return await repo.get_all()

@router.post("/verificar", response_model=Dict[str, Any])
async def check_medicamento_safety(
    medicamento: MedicamentoCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Analisa previamente a segurança de um medicamento antes de criar.
    Retorna alertas de interação e riscos geriátricos.
    """
    repo = MedicamentoRepository(db)
    clinical = ClinicalService(db)
    
    # 1. Tentar identificar o medicamento no catálogo
    catalogo_match = await repo.search_by_name(medicamento.nome)
    
    if not catalogo_match:
        return {
            "status": "unknown",
            "message": "Medicamento não encontrado no catálogo oficial. A análise de risco não pode ser realizada.",
            "alerts": []
        }
        
    catalogo_id = catalogo_match['id']
    
    # 2. Executar análise de segurança
    safety_report = await clinical.full_safety_check(
        idoso_id=medicamento.idoso_id,
        catalogo_id=catalogo_id,
        dosage=medicamento.dosagem
    )
    
    # Adicionar dados do medicamento identificado
    safety_report['identified_drug'] = catalogo_match['nome']
    
    return safety_report

@router.get("/{idoso_id}", response_model=List[MedicamentoResponse])
async def list_medicamentos(idoso_id: int, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Lista medicamentos. Regra: como passa idoso_id, limita a 1 item."""
    repo = MedicamentoRepository(db)
    results = await repo.get_by_idoso(idoso_id)
    return results[:1]


@router.post("/", response_model=MedicamentoResponse)
async def create_medicamento(medicamento: MedicamentoCreate, db: AsyncSession = Depends(get_db), current_user: dict = Depends(check_role(["admin", "attendant", "family"]))):
    repo = MedicamentoRepository(db)
    
    # Preparar dados
    med_data = medicamento.model_dump()
    
    # Tentar vincular automaticamente ao catálogo (Vital Link)
    catalogo_match = await repo.search_by_name(medicamento.nome)
    if catalogo_match:
        med_data['catalogo_ref_id'] = catalogo_match['id']
        # Se não tiver princípio ativo preenchido, preencher com o oficial
        if not med_data.get('principio_ativo'):
            med_data['principio_ativo'] = catalogo_match['nome'] # Nome oficial costuma ser princ ativo
            
        # 3. Executar análise de segurança (Alerta Família)
        clinical = ClinicalService(db)
        safety = await clinical.full_safety_check(
            idoso_id=medicamento.idoso_id,
            catalogo_id=med_data['catalogo_ref_id'],
            dosage=medicamento.dosagem
        )
        
        # Se for PERIGOSO, criar alerta para família imediatamente
        if safety['status'] == 'danger':
            alerta_repo = AlertaRepository(db)
            # Filtra apenas alertas graves para o push
            alerts_text = " | ".join([a['message'] for a in safety['alerts'] if a['severity'] in ['FATAL', 'ALTO', 'GRAVE']])
            
            await alerta_repo.create_alerta(
                idoso_id=medicamento.idoso_id,
                tipo="risco_medicamentoso",
                severidade="critica",
                mensagem=f"ALERTA DE SEGURANÇA: O medicamento '{medicamento.nome}' foi adicionado, mas apresenta RISCOS GRAVES: {alerts_text}",
                destinatarios=["familia", "responsavel"]
            )
            
    return await repo.create(med_data)


@router.delete("/{id}", response_model=MessageResponse)
async def delete_medicamento(id: int, db: AsyncSession = Depends(get_db), current_user: dict = Depends(check_role(["admin", "attendant"]))):
    repo = MedicamentoRepository(db)
    success = await repo.delete(id)
    if not success:
        raise HTTPException(status_code=404, detail="Medicamento not found")
    return {"message": "Medicamento disabled"}

@router.post("/confirmar", response_model=MessageResponse)
async def confirm_medicamento(id: int, agendamento_id: int, db: AsyncSession = Depends(get_db)):
    repo = MedicamentoRepository(db)
    await repo.confirm_intake(id, agendamento_id)
    return {"message": "Confirmed"}

# --- Sinais Vitais ---

@router.get("/sinais-vitais/{idoso_id}", response_model=List[SinaisVitaisResponse])
async def list_sinais_vitais(idoso_id: int, db: AsyncSession = Depends(get_db)):
    """Lista sinais vitais. Regra: como passa idoso_id, limita a 1 item."""
    repo = SinaisVitaisRepository(db)
    results = await repo.get_by_idoso(idoso_id)
    return results[:1]

@router.post("/sinais-vitais", response_model=SinaisVitaisResponse)
async def create_sinal_vital(sinal: SinaisVitaisCreate, db: AsyncSession = Depends(get_db)):
    repo = SinaisVitaisRepository(db)
    return await repo.create(sinal.model_dump())

@router.get("/sinais-vitais/relatorio/{idoso_id}", response_model=List[SinaisVitaisResponse])
async def get_relatorio_sinais(idoso_id: int, db: AsyncSession = Depends(get_db)):
    repo = SinaisVitaisRepository(db)
    return await repo.get_weekly_report(idoso_id)
