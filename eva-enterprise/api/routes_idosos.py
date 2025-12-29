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
        db: AsyncSession = Depends(get_db)
):
    """Lista idosos. Regra: se algum filtro for passado, retorna 1. Se não, retorna 10 por padrão."""
    if limit is None:
        limit = 1 if (nome or cpf or telefone) else 10

    repo = IdosoRepository(db)
    return await repo.get_all(skip=skip, limit=limit, nome=nome, cpf=cpf, telefone=telefone)


@router.get("/{id}", response_model=IdosoResponse)
async def get_idoso(id: int, db: AsyncSession = Depends(get_db)):
    repo = IdosoRepository(db)
    idoso = await repo.get_by_id(id)
    if not idoso:
        raise HTTPException(status_code=404, detail="Idoso not found")
    return idoso


@router.post("/", response_model=IdosoResponse)
async def create_idoso(idoso: IdosoCreate, db: AsyncSession = Depends(get_db)):
    repo = IdosoRepository(db)
    if await repo.get_by_telefone(idoso.telefone):
        raise HTTPException(status_code=400, detail="Telefone already registered")
    return await repo.create(idoso.model_dump())


@router.put("/{id}", response_model=IdosoResponse)
async def update_idoso(id: int, idoso: IdosoUpdate, db: AsyncSession = Depends(get_db)):
    repo = IdosoRepository(db)
    updated = await repo.update(id, idoso.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Idoso not found")
    return updated


@router.delete("/{id}")
async def delete_idoso(id: int, db: AsyncSession = Depends(get_db)):
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