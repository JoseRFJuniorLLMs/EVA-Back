"""
Rotas para gerenciamento de usuários do sistema de saúde
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database.connection import get_db
from database.repositories import repository_saude
from schemas import UsuarioCreate, UsuarioUpdate, UsuarioResponse

router = APIRouter()


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def criar_usuario(
    usuario: UsuarioCreate,
    db: AsyncSession = Depends(get_db)
):
    """Cadastro de novo usuário"""
    # Verificar se email já existe
    if usuario.email:
        existing = await repository_saude.get_usuario_by_email(db, usuario.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado"
            )
    
    return await repository_saude.create_usuario(db, usuario)


@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def obter_usuario(
    usuario_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Recuperar perfil do usuário"""
    usuario = await repository_saude.get_usuario_by_id(db, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    return usuario


@router.put("/{usuario_id}", response_model=UsuarioResponse)
async def atualizar_usuario(
    usuario_id: int,
    usuario_update: UsuarioUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Atualizar dados do perfil"""
    usuario = await repository_saude.update_usuario(db, usuario_id, usuario_update)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    return usuario
