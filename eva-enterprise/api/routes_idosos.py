from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db
from database.repositories.idoso_repo import IdosoRepository
from schemas import (
    IdosoResponse, IdosoCreate, IdosoUpdate,
    FamiliarResponse, FamiliarCreate, FamiliarUpdate,
    LegadoDigitalResponse, LegadoDigitalCreate
)
from typing import List

router = APIRouter()


# --- Idosos ---

@router.get("/", response_model=List[IdosoResponse])
async def list_idosos(nome: str = None, cpf: str = None, telefone: str = None, skip: int = 0, limit: int = 10,
                db: AsyncSession = Depends(get_db)):
    repo = IdosoRepository(db)
    # Filtros agora são processados no banco de dados (Repository)
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
    # Check if idoso exists
    if not await repo.get_by_id(id):
        raise HTTPException(status_code=404, detail="Idoso not found")
    return await repo.get_familiares(id)


@router.post("/{id}/familiares", response_model=FamiliarResponse)
async def add_familiar(id: int, familiar: FamiliarCreate, db: AsyncSession = Depends(get_db)):
    repo = IdosoRepository(db)
    if not await repo.get_by_id(id):
        raise HTTPException(status_code=404, detail="Idoso not found")
    return await repo.add_familiar(id, familiar.model_dump())


@router.put("/familiares/{id}", response_model=FamiliarResponse)
async def update_familiar(id: int, familiar: FamiliarUpdate, db: AsyncSession = Depends(get_db)):
    repo = IdosoRepository(db)
    updated = await repo.update_familiar(id, familiar.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Familiar not found")
    return updated


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


@router.delete("/legado-digital/{id}")
async def remove_legado(id: int, db: AsyncSession = Depends(get_db)):
    repo = IdosoRepository(db)
    success = await repo.remove_legado(id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted"}

# Placeholder for file upload logic if needed
# @router.post("/idosos/{id}/legado-digital/upload")
# async def upload_legado(id: int, file: UploadFile = File(...), ...):
#     ...
