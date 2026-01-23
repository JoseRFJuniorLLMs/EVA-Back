from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db
from database.repositories.idoso_repo import IdosoRepository
from database.repositories.perfil_repo import PerfilRepository
from schemas import (
    IdosoResponse, IdosoCreate, IdosoUpdate,
    FamiliarResponse, FamiliarCreate,
    LegadoDigitalResponse, LegadoDigitalCreate,
    PerfilClinicoResponse, PerfilClinicoBase,
    MemoriaResponse, MemoriaBase
)
from typing import List, Optional
from utils.security import get_current_user, check_role

router = APIRouter()


# --- ROTAS ESPECÍFICAS (TEXTO) DEVEM VIR PRIMEIRO ---

@router.get("/by-cpf/{cpf}", response_model=IdosoResponse)
async def get_idoso_by_cpf(cpf: str, db: AsyncSession = Depends(get_db)):
    """
    Busca idoso pelo CPF.
    ATENÇÃO: Esta rota DEVE ficar antes das rotas com /{id}
    """
    repo = IdosoRepository(db)

    # Remove formatação do CPF (pontos, traços)
    cpf_clean = ''.join(filter(str.isdigit, cpf))

    # Busca na lista filtrando por CPF
    idosos = await repo.get_all(skip=0, limit=1, cpf=cpf_clean)

    if not idosos or len(idosos) == 0:
        raise HTTPException(status_code=404, detail=f"Idoso com CPF {cpf} não encontrado")

    return idosos[0]


@router.patch("/sync-token-by-cpf")
async def sync_token_cpf(cpf: str, token: str, db: AsyncSession = Depends(get_db)):
    """
    Sincroniza o token via CPF.
    ATENÇÃO: Esta rota DEVE ficar antes das rotas com /{id}
    """
    repo = IdosoRepository(db)
    
    # Remove formatação (pontos e traços) antes de enviar para o repositório
    cpf_clean = ''.join(filter(str.isdigit, cpf))
    
    if await repo.update_token_by_cpf(cpf_clean, token):
        return {"status": "success", "message": f"Token do CPF {cpf_clean} atualizado"}
        
    raise HTTPException(status_code=404, detail="CPF não encontrado ou erro na atualização")

# --- ROTAS GERAIS E DINÂMICAS (IDs) ---

@router.get("/", response_model=List[IdosoResponse])
async def list_idosos(
        nome: str = None,
        cpf: str = None,
        telefone: str = None,
        skip: int = 0,
        limit: int = None,
        db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """
    Lista idosos com base no perfil do usuário:
    - Admin/Profissional: Vê TODOS os idosos
    - Cuidador/Família: Vê APENAS seus idosos vinculados
    """
    from sqlalchemy import text
    
    if limit is None:
        limit = 1 if (nome or cpf or telefone) else 10

    user_id = current_user.get('user_id')
    user_role = current_user.get('role', 'cuidador')  # Default: cuidador
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")
    
    # Admin e Profissional veem TUDO
    if user_role in ['admin', 'profissional']:
        query = text("""
            SELECT i.*
            FROM idosos i
            WHERE i.ativo = true
            AND (:nome::text IS NULL OR LOWER(i.nome) LIKE LOWER(:nome_pattern))
            AND (:cpf::text IS NULL OR i.cpf = :cpf)
            AND (:telefone::text IS NULL OR i.telefone = :telefone)
            ORDER BY i.id DESC
            LIMIT :limit OFFSET :skip
        """)
        
        params = {
            "nome": nome,
            "nome_pattern": f"%{nome}%" if nome else None,
            "cpf": cpf,
            "telefone": telefone,
            "limit": limit,
            "skip": skip
        }
    else:
        # Cuidador/Família veem APENAS seus idosos
        query = text("""
            SELECT DISTINCT i.*
            FROM idosos i
            INNER JOIN usuarios_idosos ui ON ui.idoso_id = i.id
            WHERE ui.usuario_id = :user_id
            AND i.ativo = true
            AND (:nome::text IS NULL OR LOWER(i.nome) LIKE LOWER(:nome_pattern))
            AND (:cpf::text IS NULL OR i.cpf = :cpf)
            AND (:telefone::text IS NULL OR i.telefone = :telefone)
            ORDER BY i.id DESC
            LIMIT :limit OFFSET :skip
        """)
        
        params = {
            "user_id": user_id,
            "nome": nome,
            "nome_pattern": f"%{nome}%" if nome else None,
            "cpf": cpf,
            "telefone": telefone,
            "limit": limit,
            "skip": skip
        }
    
    result = await db.execute(query, params)
    idosos = result.mappings().all()
    
    return [dict(idoso) for idoso in idosos]


@router.get("/{id}", response_model=IdosoResponse)
async def get_idoso(id: int, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    repo = IdosoRepository(db)
    idoso = await repo.get_by_id(id)
    if not idoso:
        raise HTTPException(status_code=404, detail="Idoso not found")
    return idoso


@router.post("/", response_model=IdosoResponse)
async def create_idoso(idoso: IdosoCreate, db: AsyncSession = Depends(get_db), current_user: dict = Depends(check_role(["admin", "attendant"]))):
    repo = IdosoRepository(db)
    if await repo.get_by_telefone(idoso.telefone):
        raise HTTPException(status_code=400, detail="Telefone already registered")
    return await repo.create(idoso.model_dump())


@router.put("/{id}", response_model=IdosoResponse)
async def update_idoso(id: int, idoso: IdosoUpdate, db: AsyncSession = Depends(get_db), current_user: dict = Depends(check_role(["admin", "attendant"]))):
    repo = IdosoRepository(db)
    updated = await repo.update(id, idoso.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Idoso not found")
    return updated


@router.delete("/{id}")
async def delete_idoso(id: int, db: AsyncSession = Depends(get_db), current_user: dict = Depends(check_role(["admin"]))):
    repo = IdosoRepository(db)
    success = await repo.delete(id)
    if not success:
        raise HTTPException(status_code=404, detail="Idoso not found")
    return {"message": "Idoso deleted"}


# --- Familiares ---

@router.get("/{id}/familiares", response_model=List[FamiliarResponse])
async def list_familiares(id: int, db: AsyncSession = Depends(get_db)):
    repo = IdosoRepository(db)
    if not await repo.get_by_id(id):
        raise HTTPException(status_code=404, detail="Idoso not found")
    return await repo.get_familiares(id)


@router.post("/{id}/familiares", response_model=FamiliarResponse)
async def add_familiar(id: int, familiar: FamiliarCreate, db: AsyncSession = Depends(get_db)):
    repo = IdosoRepository(db)
    if not await repo.get_by_id(id):
        raise HTTPException(status_code=404, detail="Idoso not found")
    return await repo.add_familiar(id, familiar.model_dump())


# --- Legado Digital ---

@router.get("/{id}/legado-digital", response_model=List[LegadoDigitalResponse])
async def list_legado(id: int, db: AsyncSession = Depends(get_db)):
    repo = IdosoRepository(db)
    if not await repo.get_by_id(id):
        raise HTTPException(status_code=404, detail="Idoso not found")
    return await repo.get_legado(id)


@router.post("/{id}/legado-digital", response_model=LegadoDigitalResponse)
async def add_legado(id: int, legado: LegadoDigitalCreate, db: AsyncSession = Depends(get_db)):
    repo = IdosoRepository(db)
    if not await repo.get_by_id(id):
        raise HTTPException(status_code=404, detail="Idoso not found")
    return await repo.add_legado(id, legado.model_dump())


# --- Perfil Clínico e Memórias ---

@router.get("/{id}/perfil-clinico", response_model=PerfilClinicoResponse)
async def get_perfil(id: int, db: AsyncSession = Depends(get_db)):
    repo = PerfilRepository(db)
    perfil = await repo.get_perfil_clinico(id)
    if not perfil:
        raise HTTPException(status_code=404, detail="Perfil Clínico not found")
    return perfil


@router.post("/{id}/perfil-clinico", response_model=PerfilClinicoResponse)
async def update_perfil(id: int, data: PerfilClinicoBase, db: AsyncSession = Depends(get_db)):
    repo = PerfilRepository(db)
    return await repo.update_perfil_clinico(id, data.model_dump())


@router.get("/{id}/memorias", response_model=List[MemoriaResponse])
async def list_memorias(id: int, categoria: str = None, db: AsyncSession = Depends(get_db)):
    repo = PerfilRepository(db)
    return await repo.get_memorias(id, categoria)


@router.post("/{id}/memorias", response_model=MemoriaResponse)
async def add_memoria(id: int, data: MemoriaBase, db: AsyncSession = Depends(get_db)):
    repo = PerfilRepository(db)
    return await repo.add_memoria(id, data.categoria, data.chave, data.valor, data.relevancia)


@router.patch("/{id}/device-token")
async def update_idoso_device_token(
        id: int,
        token: str,
        db: AsyncSession = Depends(get_db)
):
    """
    Endpoint para o App Flutter sincronizar o FCM Token do idoso pelo ID.
    """
    repo = IdosoRepository(db)
    success = await repo.update_device_token(id, token)
    if not success:
        raise HTTPException(status_code=400, detail="Erro ao atualizar o token do dispositivo")
    return {"status": "success", "message": "Token atualizado corretamente"}


@router.post("/{id}/notify")
async def notify_idoso(id: int, title: str, body: str, db: AsyncSession = Depends(get_db)):
    """
    Envia uma notificação push direta para o idoso.
    """
    repo = IdosoRepository(db)
    idoso = await repo.get_by_id(id)
    if not idoso or not idoso.device_token:
        raise HTTPException(status_code=404, detail="Idoso não encontrado ou sem device_token")
    
    from services.notification_service import NotificationService
    notifier = NotificationService()
    success = notifier.send_push_notification(
        token=idoso.device_token,
        title=title,
        body=body,
        data={"type": "generic_notification"}
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Falha ao enviar notificação")
        
    return {"status": "success", "message": "Notificação enviada"}


@router.post("/{id}/sync-device")
async def sync_device_data(id: int, db: AsyncSession = Depends(get_db)):
    """
    Envia um 'Silent Push' para o dispositivo do idoso,
    forçando o EVA-Mobile a coletar dados de saúde (Health Connect) e enviar para o backend.
    """
    repo = IdosoRepository(db)
    idoso = await repo.get_by_id(id)
    if not idoso or not idoso.device_token:
        raise HTTPException(status_code=404, detail="Idoso não encontrado ou sem device_token")
    
    from services.notification_service import NotificationService
    notifier = NotificationService()
    
    # Payload específico que o App reconhece para iniciar o sync
    data_payload = {
        "action": "HEALTH_SYNC",
        "idosoId": str(id)
    }
    
    success = notifier.send_silent_data_message(
        token=idoso.device_token,
        data=data_payload
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Falha ao enviar comando de sincronização")
        
    return {"status": "success", "message": "Comando de sincronização enviado"}


# ==================== SEMANTIC MEMORY SEARCH ====================

@router.get("/{id}/memorias/search", tags=["Idosos"])
async def search_memories(
    id: int,
    q: str = Query(..., description="Termo de busca semântica"),
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """Busca memórias usando busca vetorial (se disponível) ou texto"""
    from sqlalchemy import text
    
    # Tentativa de busca vetorial se a função existir, caso contrário fallback para texto
    try:
        # Fallback para busca por texto simples
        result = await db.execute(text("""
            SELECT id, content, speaker, timestamp, emotion, 1.0 as similarity
            FROM episodic_memories 
            WHERE idoso_id = :id AND content ILIKE :q
            LIMIT :limit
        """), {"id": id, "q": f"%{q}%", "limit": limit})
        
        return [dict(row._mapping) for row in result.all()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

