from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.connection import get_db
from database.repositories.config_repo import ConfigRepository
from schemas import (
    ConfigResponse, ConfigCreate, ConfigUpdate,
    PromptResponse, PromptCreate,
    FuncaoResponse, FuncaoCreate,
    CircuitBreakerResponse, RateLimitResponse, RateLimitUpdate
)
from typing import List

router = APIRouter()

# --- Configurations ---

@router.get("/", response_model=List[ConfigResponse])
def list_configs(db: Session = Depends(get_db)):
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

# --- Prompts ---

@router.get("/prompts", response_model=List[PromptResponse])
def list_prompts(db: Session = Depends(get_db)):
    repo = ConfigRepository(db)
    return repo.get_prompts()

@router.post("/prompts", response_model=PromptResponse)
def create_prompt(prompt: PromptCreate, db: Session = Depends(get_db)):
    repo = ConfigRepository(db)
    return repo.create_prompt(prompt.nome, prompt.template, prompt.versao)

@router.put("/prompts/{id}", response_model=PromptResponse)
def update_prompt(id: int, prompt_update: dict, db: Session = Depends(get_db)):
    # Assuming partial update for version/template
    repo = ConfigRepository(db)
    updated = repo.update_prompt(id, prompt_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return updated

# --- Funcoes ---

@router.get("/funcoes", response_model=List[FuncaoResponse])
def list_functions(db: Session = Depends(get_db)):
    repo = ConfigRepository(db)
    return repo.get_functions()

@router.post("/funcoes", response_model=FuncaoResponse)
def create_function(func: FuncaoCreate, db: Session = Depends(get_db)):
    repo = ConfigRepository(db)
    return repo.create_function(func.nome, func.descricao, func.parameters, func.tipo_tarefa)

# --- Circuit Breakers ---

@router.get("/circuit-breakers", response_model=List[CircuitBreakerResponse])
def list_circuit_breakers(db: Session = Depends(get_db)):
    repo = ConfigRepository(db)
    return repo.get_circuit_breakers()

@router.post("/circuit-breakers/reset/{id}", response_model=CircuitBreakerResponse)
def reset_circuit_breaker(id: int, db: Session = Depends(get_db)):
    repo = ConfigRepository(db)
    cb = repo.reset_circuit_breaker(id)
    if not cb:
        raise HTTPException(status_code=404, detail="Circuit Breaker not found")
    return cb

# --- Rate Limits ---

@router.get("/rate-limits", response_model=List[RateLimitResponse])
def list_rate_limits(db: Session = Depends(get_db)):
    repo = ConfigRepository(db)
    return repo.get_rate_limits()

@router.put("/rate-limits/{id}", response_model=RateLimitResponse)
def update_rate_limit(id: int, limit: RateLimitUpdate, db: Session = Depends(get_db)):
    repo = ConfigRepository(db)
    updated = repo.update_rate_limit(id, limit.limit_count, limit.interval_seconds)
    if not updated:
        raise HTTPException(status_code=404, detail="Rate Limit not found")
    return updated
