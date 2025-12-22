from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
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

@router.get("/idosos", response_model=List[IdosoResponse])
def list_idosos(nome: str = None, telefone: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    repo = IdosoRepository(db)
    # Basic filtering logic could be improved in repo
    all_idosos = repo.get_all(skip=skip, limit=limit)
    if nome:
        all_idosos = [i for i in all_idosos if nome.lower() in i.nome.lower()]
    if telefone:
        all_idosos = [i for i in all_idosos if telefone in i.telefone]
    return all_idosos

@router.get("/idosos/{id}", response_model=IdosoResponse)
def get_idoso(id: int, db: Session = Depends(get_db)):
    repo = IdosoRepository(db)
    idoso = repo.get_by_id(id)
    if not idoso:
        raise HTTPException(status_code=404, detail="Idoso not found")
    return idoso

@router.post("/idosos", response_model=IdosoResponse)
def create_idoso(idoso: IdosoCreate, db: Session = Depends(get_db)):
    repo = IdosoRepository(db)
    if repo.get_by_telefone(idoso.telefone):
        raise HTTPException(status_code=400, detail="Telefone already registered")
    return repo.create(idoso.model_dump())

@router.put("/idosos/{id}", response_model=IdosoResponse)
def update_idoso(id: int, idoso: IdosoUpdate, db: Session = Depends(get_db)):
    repo = IdosoRepository(db)
    updated = repo.update(id, idoso.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Idoso not found")
    return updated

@router.delete("/idosos/{id}")
def delete_idoso(id: int, db: Session = Depends(get_db)):
    repo = IdosoRepository(db)
    success = repo.delete(id)
    if not success:
        raise HTTPException(status_code=404, detail="Idoso not found")
    return {"message": "Idoso deleted"}

# --- Familiares ---

@router.get("/idosos/{id}/familiares", response_model=List[FamiliarResponse])
def list_familiares(id: int, db: Session = Depends(get_db)):
    repo = IdosoRepository(db)
    # Check if idoso exists
    if not repo.get_by_id(id):
        raise HTTPException(status_code=404, detail="Idoso not found")
    return repo.get_familiares(id)

@router.post("/idosos/{id}/familiares", response_model=FamiliarResponse)
def add_familiar(id: int, familiar: FamiliarCreate, db: Session = Depends(get_db)):
    repo = IdosoRepository(db)
    if not repo.get_by_id(id):
        raise HTTPException(status_code=404, detail="Idoso not found")
    return repo.add_familiar(id, familiar.model_dump())

@router.put("/familiares/{id}", response_model=FamiliarResponse)
def update_familiar(id: int, familiar: FamiliarUpdate, db: Session = Depends(get_db)):
    repo = IdosoRepository(db)
    updated = repo.update_familiar(id, familiar.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Familiar not found")
    return updated

# --- Legado Digital ---

@router.get("/idosos/{id}/legado-digital", response_model=List[LegadoDigitalResponse])
def list_legado(id: int, db: Session = Depends(get_db)):
    repo = IdosoRepository(db)
    if not repo.get_by_id(id):
        raise HTTPException(status_code=404, detail="Idoso not found")
    return repo.get_legado(id)

@router.post("/idosos/{id}/legado-digital", response_model=LegadoDigitalResponse)
def add_legado(id: int, legado: LegadoDigitalCreate, db: Session = Depends(get_db)):
    repo = IdosoRepository(db)
    if not repo.get_by_id(id):
        raise HTTPException(status_code=404, detail="Idoso not found")
    return repo.add_legado(id, legado.model_dump())

@router.delete("/legado-digital/{id}")
def remove_legado(id: int, db: Session = Depends(get_db)):
    repo = IdosoRepository(db)
    success = repo.remove_legado(id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted"}

# Placeholder for file upload logic if needed
# @router.post("/idosos/{id}/legado-digital/upload")
# async def upload_legado(id: int, file: UploadFile = File(...), ...):
#     ...
