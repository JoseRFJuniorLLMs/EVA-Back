from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db
from database.repositories.cuidador_repo import CuidadorRepository
from schemas import CuidadorResponse, CuidadorCreate, CuidadorUpdate
from typing import List, Optional

router = APIRouter()


# =====================================================
# ROTAS ESPECÍFICAS (DEVEM VIR PRIMEIRO)
# =====================================================

@router.get("/by-cpf/{cpf}", response_model=CuidadorResponse)
async def get_cuidador_by_cpf(cpf: str, db: AsyncSession = Depends(get_db)):
    """
    Busca cuidador pelo CPF.
    Aceita CPF formatado (XXX.XXX.XXX-XX) ou apenas números.
    """
    repo = CuidadorRepository(db)
    cuidador = await repo.get_by_cpf(cpf)
    if not cuidador:
        raise HTTPException(status_code=404, detail=f"Cuidador com CPF {cpf} não encontrado")
    return cuidador


@router.get("/idoso/{idoso_id}", response_model=List[CuidadorResponse])
async def list_cuidadores_by_idoso(
    idoso_id: int,
    ativo: Optional[bool] = True,
    db: AsyncSession = Depends(get_db)
):
    """
    Lista todos os cuidadores de um idoso específico.
    Retorna ordenado por prioridade.
    """
    repo = CuidadorRepository(db)
    return await repo.get_by_idoso(idoso_id, ativo)


@router.get("/emergencia/{idoso_id}", response_model=List[CuidadorResponse])
async def get_emergencia_contacts(idoso_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retorna apenas os contatos marcados como emergência.
    Ordenado por prioridade (1=mais alta).
    """
    repo = CuidadorRepository(db)
    contatos = await repo.get_emergencia_contacts(idoso_id)
    if not contatos:
        raise HTTPException(
            status_code=404,
            detail=f"Nenhum contato de emergência encontrado para idoso {idoso_id}"
        )
    return contatos


@router.get("/responsavel/{idoso_id}", response_model=CuidadorResponse)
async def get_responsavel(idoso_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retorna o responsável legal do idoso.
    """
    repo = CuidadorRepository(db)
    responsavel = await repo.get_responsavel(idoso_id)
    if not responsavel:
        raise HTTPException(
            status_code=404,
            detail=f"Responsável não encontrado para idoso {idoso_id}"
        )
    return responsavel


@router.patch("/sync-token-by-cpf")
async def sync_token_cpf(cpf: str, token: str, db: AsyncSession = Depends(get_db)):
    """
    Sincroniza o token Firebase via CPF.
    Útil para apps mobile que só conhecem o CPF do cuidador.
    """
    repo = CuidadorRepository(db)
    
    # Remove formatação do CPF
    cpf_clean = ''.join(filter(str.isdigit, cpf))
    
    if await repo.update_token_by_cpf(cpf_clean, token):
        return {
            "status": "success",
            "message": f"Token atualizado para CPF {cpf_clean}"
        }
    
    raise HTTPException(
        status_code=404,
        detail="CPF não encontrado ou erro na atualização"
    )


# =====================================================
# ROTAS GERAIS E DINÂMICAS (IDs)
# =====================================================

@router.get("/", response_model=List[CuidadorResponse])
async def list_cuidadores(
    skip: int = 0,
    limit: int = 10,
    idoso_id: Optional[int] = None,
    tipo_cuidador: Optional[str] = None,
    ativo: Optional[bool] = True,
    db: AsyncSession = Depends(get_db)
):
    """
    Lista cuidadores com filtros opcionais.
    
    Filtros disponíveis:
    - idoso_id: Filtra por idoso específico
    - tipo_cuidador: familiar, profissional ou voluntario
    - ativo: true (padrão) ou false
    """
    repo = CuidadorRepository(db)
    return await repo.get_all(skip, limit, idoso_id, tipo_cuidador, ativo)


@router.get("/{id}", response_model=CuidadorResponse)
async def get_cuidador(id: int, db: AsyncSession = Depends(get_db)):
    """Busca cuidador por ID"""
    repo = CuidadorRepository(db)
    cuidador = await repo.get_by_id(id)
    if not cuidador:
        raise HTTPException(status_code=404, detail="Cuidador não encontrado")
    return cuidador


@router.post("/", response_model=CuidadorResponse, status_code=201)
async def create_cuidador(cuidador: CuidadorCreate, db: AsyncSession = Depends(get_db)):
    """
    Cria novo cuidador.
    
    Campos obrigatórios:
    - idoso_id
    - nome
    - telefone
    """
    repo = CuidadorRepository(db)
    return await repo.create(cuidador.model_dump())


@router.put("/{id}", response_model=CuidadorResponse)
async def update_cuidador(
    id: int,
    cuidador: CuidadorUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Atualiza cuidador (atualização parcial).
    Apenas os campos enviados serão atualizados.
    """
    repo = CuidadorRepository(db)
    updated = await repo.update(id, cuidador.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Cuidador não encontrado")
    return updated


@router.patch("/{id}/device-token")
async def update_device_token(
    id: int,
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Atualiza apenas o token do dispositivo Firebase.
    Endpoint usado pelo app mobile para sincronizar FCM token.
    """
    repo = CuidadorRepository(db)
    if not await repo.update_device_token(id, token):
        raise HTTPException(
            status_code=404,
            detail="Cuidador não encontrado"
        )
    return {
        "status": "success",
        "message": "Token do dispositivo atualizado com sucesso"
    }


@router.delete("/{id}")
async def delete_cuidador(id: int, db: AsyncSession = Depends(get_db)):
    """
    Soft delete - marca o cuidador como inativo.
    O registro permanece no banco mas ativo=false.
    """
    repo = CuidadorRepository(db)
    if not await repo.delete(id):
        raise HTTPException(status_code=404, detail="Cuidador não encontrado")
    return {
        "message": "Cuidador desativado com sucesso"
    }
