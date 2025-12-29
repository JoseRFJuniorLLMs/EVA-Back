import os
import uvicorn
import logging
import subprocess
from dotenv import load_dotenv

# FastAPI
from fastapi import FastAPI, Query
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
    routes_placeholders,
    routes_protocolos,
    routes_historico
)

load_dotenv()

# ==========================
# CONFIGURAÇÕES
# ==========================
# AJUSTE: Mudei o padrão para 8000 para bater com seus testes e o Flutter
PORT = int(os.getenv("PORT", "8000"))

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
# CORS (A PARTE MAIS IMPORTANTE AGORA)
# ======================
# Isso garante que o Flutter Web (browser) consiga falar com o Back
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Libera geral (Web, Localhost, IP)
    allow_credentials=True,
    allow_methods=["*"],  # Libera GET, POST, PUT, PATCH, DELETE, OPTIONS
    allow_headers=["*"],  # Libera todos os cabeçalhos
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
app.include_router(routes_protocolos.router, prefix="/protocolos", tags=["Protocolos"])
app.include_router(routes_historico.router, prefix="/historico", tags=["Histórico"])
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
        "architecture": "Full Async",
        "cors_enabled": True
    }


@app.get("/", tags=["Root"])
async def root():
    """Endpoint raiz"""
    return {
        "message": "EVA Enterprise API - Sistema de Cuidados com Idosos (Async)",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/sistema/logs")
async def obter_logs(linhas: int = Query(50, ge=1, le=500)):
    """
    Rota para monitoramento técnico do serviço via terminal
    """
    try:
        # Executa o comando journalctl para ler o próprio serviço
        # Importante: o usuário 'web2ajax' precisa ter permissão de ler logs
        comando = ["journalctl", "-u", "eva-backend.service", "-n", str(linhas), "--no-pager"]
        resultado = subprocess.check_output(comando).decode("utf-8")

        # Converte a saída em uma lista de strings (JSON format)
        log_lista = resultado.strip().split("\n")

        return {
            "servico": "eva-backend",
            "status": "online",
            "logs": log_lista
        }
    except Exception as e:
        return {"erro": f"Falha ao ler logs: {str(e)}"}


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
    # Host 0.0.0.0 é obrigatório para funcionar na GCP e receber conexões externas
    uvicorn.run(app, host="0.0.0.0", port=PORT)