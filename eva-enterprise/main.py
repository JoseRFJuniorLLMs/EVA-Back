import os
import uvicorn
import logging
from dotenv import load_dotenv

# FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Banco de dados
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db

# Import routers
from api import (
    routes_idosos,
    routes_agendamentos,
    routes_alertas,
    routes_medicamentos,
    routes_pagamentos,
    routes_config,
    routes_extras,
    routes_orquestrador,
    routes_placeholders
)

load_dotenv()

# ==========================
# CONFIGURAÇÕES
# ==========================
PORT = int(os.getenv("PORT", "8080"))

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializa FastAPI
app = FastAPI(
    title="EVA Enterprise API",
    description="API assíncrona para gerenciamento de cuidados com idosos",
    version="2.0.0"
)

# ======================
# CORS
# ======================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ======================
# ROTAS
# ======================
app.include_router(routes_idosos.router, prefix="/idosos", tags=["Idosos"])
app.include_router(routes_agendamentos.router, prefix="/agendamentos", tags=["Agendamentos"])
app.include_router(routes_alertas.router, prefix="/alertas", tags=["Alertas"])
app.include_router(routes_medicamentos.router, prefix="/medicamentos", tags=["Medicamentos"])
app.include_router(routes_pagamentos.router, prefix="/pagamentos", tags=["Pagamentos"])
app.include_router(routes_config.router, prefix="/config", tags=["Configurações"])
app.include_router(routes_extras.router, prefix="/extras", tags=["Extras"])
app.include_router(routes_orquestrador.router, prefix="/orquestrador", tags=["Orquestrador"])
app.include_router(routes_placeholders.router, tags=["Placeholders"])


# ======================
# HEALTH CHECK
# ======================
@app.get("/health", tags=["Health"])
async def health_check():
    """Endpoint para verificar saúde da API"""
    return {
        "status": "healthy",
        "service": "EVA Enterprise API",
        "version": "2.0.0",
        "architecture": "Full Async"
    }


@app.get("/", tags=["Root"])
async def root():
    """Endpoint raiz"""
    return {
        "message": "EVA Enterprise API - Sistema de Cuidados com Idosos (Async)",
        "docs": "/docs",
        "health": "/health"
    }


# ==========================
# INÍCIO
# ==========================
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 EVA Enterprise API (Full Async)")
    print("=" * 60)
    print(f"Porta: {PORT}")
    print(f"Documentação: http://localhost:{PORT}/docs")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=PORT)
