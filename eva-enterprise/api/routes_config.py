from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db
from database.repositories.config_repo import ConfigRepository
from typing import List

router = APIRouter()


# --- Prompts ---

@router.get("/prompts/", response_model=List[dict])
async def list_prompts(db: AsyncSession = Depends(get_db)):
    repo = ConfigRepository(db)
    return await repo.get_prompts()

@router.post("/prompts/", response_model=dict)
async def create_prompt(nome: str, template: str, versao: str, db: AsyncSession = Depends(get_db)):
    repo = ConfigRepository(db)
    return await repo.create_prompt(nome, template, versao)

@router.put("/prompts/{id}", response_model=dict)
async def update_prompt(id: int, prompt_update: dict, db: AsyncSession = Depends(get_db)):
    # Assuming partial update for version/template
    repo = ConfigRepository(db)
    updated = await repo.update_prompt(id, prompt_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return updated

# --- Functions ---

@router.get("/functions/", response_model=List[dict])
async def list_functions(db: AsyncSession = Depends(get_db)):
    repo = ConfigRepository(db)
    return await repo.get_functions()

@router.post("/functions/", response_model=dict)
async def create_function(nome: str, descricao: str, parameters: dict, tipo: str, db: AsyncSession = Depends(get_db)):
    repo = ConfigRepository(db)
    return await repo.create_function(nome, descricao, parameters, tipo)

# --- Circuit Breakers ---

@router.get("/circuit-breakers/", response_model=List[dict])
async def list_circuit_breakers(db: AsyncSession = Depends(get_db)):
    repo = ConfigRepository(db)
    return await repo.get_circuit_breakers()

@router.post("/circuit-breakers/{id}/reset", response_model=dict)
async def reset_circuit_breaker(id: int, db: AsyncSession = Depends(get_db)):
    repo = ConfigRepository(db)
    cb = await repo.reset_circuit_breaker(id)
    if not cb:
        raise HTTPException(status_code=404, detail="Circuit breaker not found")
    return cb

# --- Rate Limits ---

@router.get("/rate-limits/", response_model=List[dict])
async def list_rate_limits(db: AsyncSession = Depends(get_db)):
    repo = ConfigRepository(db)
    return await repo.get_rate_limits()

@router.put("/rate-limits/{id}", response_model=dict)
async def update_rate_limit(id: int, limit: int, interval: int, db: AsyncSession = Depends(get_db)):
    repo = ConfigRepository(db)
    updated = await repo.update_rate_limit(id, limit, interval)
    if not updated:
        raise HTTPException(status_code=404, detail="Rate limit not found")
    return updated

# --- Configurations (Dynamic Routes Last) ---

    repo = ConfigRepository(db)
    return repo.get_all_configs()

@router.get("/{chave}", response_model=ConfigResponse)
def get_config(chave: str, db: Session = Depends(get_db)):
    repo = ConfigRepository(db)
    config = repo.get_config_by_key(chave)
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    return config

@router.post("/", response_model=ConfigResponse)
def create_config(config: ConfigCreate, db: Session = Depends(get_db)):
    repo = ConfigRepository(db)
    # Check if exists
    if repo.get_config_by_key(config.chave):
        raise HTTPException(status_code=400, detail="Config key already exists")
    return repo.create_config(config.chave, config.valor, config.tipo, config.categoria)

@router.put("/{id}", response_model=ConfigResponse)
def update_config(id: int, config: ConfigUpdate, db: Session = Depends(get_db)):
    repo = ConfigRepository(db)
    updated = repo.update_config(id, config.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Config not found")
    return updated

@router.delete("/{id}")
def delete_config(id: int, db: Session = Depends(get_db)):
    repo = ConfigRepository(db)
    success = repo.delete_config(id)
    if not success:
        raise HTTPException(status_code=404, detail="Config not found")
    return {"message": "Config deleted"}

