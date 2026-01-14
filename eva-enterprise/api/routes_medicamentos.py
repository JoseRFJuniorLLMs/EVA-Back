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

# --- Catálogo Farmacêutico ---

@router.get("/catalogo/search")
async def search_catalogo(
    q: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Busca medicamentos no catálogo farmacêutico.
    Retorna lista de medicamentos com informações básicas.
    """
    from sqlalchemy import text
    
    query = text("""
        SELECT 
            id,
            nome_oficial,
            classe_terapeutica,
            apresentacao_padrao,
            dose_maxima_mg,
            alerta_renal
        FROM catalogo_farmaceutico
        WHERE LOWER(nome_oficial) LIKE LOWER(:search)
        LIMIT 10
    """)
    
    result = await db.execute(query, {"search": f"%{q}%"})
    medicamentos = result.mappings().all()
    
    # Para cada medicamento, buscar riscos geriátricos
    output = []
    for med in medicamentos:
        riscos_query = text("""
            SELECT tipo, ativo
            FROM riscos_geriatricos
            WHERE catalogo_id = :catalogo_id
        """)
        riscos_result = await db.execute(riscos_query, {"catalogo_id": med['id']})
        riscos = [{"tipo": r['tipo'], "ativo": r['ativo']} for r in riscos_result.mappings().all()]
        
        output.append({
            "id": med['id'],
            "nome_oficial": med['nome_oficial'],
            "classe_terapeutica": med['classe_terapeutica'] or '',
            "apresentacao_padrao": med['apresentacao_padrao'] or '',
            "dose_maxima_mg": med['dose_maxima_mg'],
            "alerta_renal": med['alerta_renal'],
            "riscos": riscos
        })
    
    return output

@router.get("/catalogo/{catalogo_id}")
async def get_catalogo_info(
    catalogo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtém informações detalhadas de um medicamento do catálogo.
    """
    from sqlalchemy import text
    
    query = text("""
        SELECT 
            id,
            nome_oficial,
            classe_terapeutica,
            apresentacao_padrao,
            dose_maxima_mg,
            alerta_renal
        FROM catalogo_farmaceutico
        WHERE id = :catalogo_id
    """)
    
    result = await db.execute(query, {"catalogo_id": catalogo_id})
    med = result.mappings().first()
    
    if not med:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado no catálogo")
    
    # Buscar riscos geriátricos
    riscos_query = text("""
        SELECT tipo, ativo, descricao
        FROM riscos_geriatricos
        WHERE catalogo_id = :catalogo_id
    """)
    riscos_result = await db.execute(riscos_query, {"catalogo_id": catalogo_id})
    riscos = [{"tipo": r['tipo'], "ativo": r['ativo'], "descricao": r['descricao']} 
              for r in riscos_result.mappings().all()]
    
    # Buscar referências de dosagem
    dosagem_query = text("""
        SELECT dose_maxima_mg, alerta_renal
        FROM referencia_dosagem
        WHERE catalogo_id = :catalogo_id
        LIMIT 1
    """)
    dosagem_result = await db.execute(dosagem_query, {"catalogo_id": catalogo_id})
    dosagem = dosagem_result.mappings().first()
    
    return {
        "id": med['id'],
        "nome_oficial": med['nome_oficial'],
        "classe_terapeutica": med['classe_terapeutica'] or '',
        "apresentacao_padrao": med['apresentacao_padrao'] or '',
        "dose_maxima_mg": dosagem['dose_maxima_mg'] if dosagem else med['dose_maxima_mg'],
        "alerta_renal": dosagem['alerta_renal'] if dosagem else med['alerta_renal'],
        "riscos": riscos
    }

@router.post("/verificar-interacoes")
async def check_interacoes(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Verifica interações medicamentosas entre o novo medicamento
    e os medicamentos atuais do idoso.
    """
    from sqlalchemy import text
    
    idoso_id = data.get('idoso_id')
    novo_medicamento = data.get('novo_medicamento')
    
    if not idoso_id or not novo_medicamento:
        raise HTTPException(status_code=400, detail="idoso_id e novo_medicamento são obrigatórios")
    
    # 1. Buscar medicamentos atuais do idoso
    medicamentos_query = text("""
        SELECT m.nome, m.catalogo_ref_id
        FROM medicamentos m
        WHERE m.idoso_id = :idoso_id
        AND m.ativo = true
    """)
    result = await db.execute(medicamentos_query, {"idoso_id": idoso_id})
    medicamentos_atuais = result.mappings().all()
    
    # 2. Buscar ID do novo medicamento no catálogo
    novo_med_query = text("""
        SELECT id FROM catalogo_farmaceutico
        WHERE LOWER(nome_oficial) LIKE LOWER(:nome)
        LIMIT 1
    """)
    novo_result = await db.execute(novo_med_query, {"nome": f"%{novo_medicamento}%"})
    novo_med = novo_result.mappings().first()
    
    if not novo_med:
        return []  # Medicamento não encontrado no catálogo, sem interações
    
    novo_catalogo_id = novo_med['id']
    
    # 3. Verificar interações
    interacoes = []
    for med_atual in medicamentos_atuais:
        if not med_atual['catalogo_ref_id']:
            continue
            
        # Buscar interação na tabela interacoes_risco
        interacao_query = text("""
            SELECT 
                ir.nivel_perigo,
                ir.descricao,
                c1.nome_oficial as med_a,
                c2.nome_oficial as med_b
            FROM interacoes_risco ir
            JOIN catalogo_farmaceutico c1 ON c1.id = ir.catalogo_id_a
            JOIN catalogo_farmaceutico c2 ON c2.id = ir.catalogo_id_b
            WHERE 
                (ir.catalogo_id_a = :cat_a AND ir.catalogo_id_b = :cat_b)
                OR (ir.catalogo_id_a = :cat_b AND ir.catalogo_id_b = :cat_a)
        """)
        
        interacao_result = await db.execute(
            interacao_query,
            {"cat_a": med_atual['catalogo_ref_id'], "cat_b": novo_catalogo_id}
        )
        interacao = interacao_result.mappings().first()
        
        if interacao:
            interacoes.append({
                "medicamento_a": interacao['med_a'],
                "medicamento_b": interacao['med_b'],
                "nivel_perigo": interacao['nivel_perigo'],
                "descricao": interacao['descricao']
            })
    
    return interacoes
