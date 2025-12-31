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
    routes_historico,
    routes_assinaturas,
    routes_ia,
    # Health Data Routes
    routes_usuarios_saude,
    routes_saude,
    routes_dashboard_saude
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
# ROTAS (Todas com prefixo /api/v1/)
# ======================

# Sistema de Cuidados com Idosos
app.include_router(routes_idosos.router, prefix="/api/v1/idosos", tags=["Idosos"])
app.include_router(routes_agendamentos.router, prefix="/api/v1/agendamentos", tags=["Agendamentos"])
app.include_router(routes_alertas.router, prefix="/api/v1/alertas", tags=["Alertas"])
app.include_router(routes_medicamentos.router, prefix="/api/v1/medicamentos", tags=["Medicamentos"])
app.include_router(routes_pagamentos.router, prefix="/api/v1/pagamentos", tags=["Pagamentos"])
app.include_router(routes_config.router, prefix="/api/v1/config", tags=["Configurações"])
app.include_router(routes_extras.router, prefix="/api/v1/extras", tags=["Extras"])
app.include_router(routes_orquestrador.router, prefix="/api/v1/orquestrador", tags=["Orquestrador"])
app.include_router(routes_protocolos.router, prefix="/api/v1/protocolos", tags=["Protocolos"])
app.include_router(routes_historico.router, prefix="/api/v1/historico", tags=["Histórico"])
app.include_router(routes_placeholders.router, prefix="/api/v1", tags=["Placeholders"])
app.include_router(routes_assinaturas.router, prefix="/api/v1/assinaturas", tags=["Assinaturas"])
app.include_router(routes_ia.router, prefix="/api/v1/ia", tags=["IA Avançada"])

# Sistema de Saúde e Bem-Estar
app.include_router(routes_usuarios_saude.router, prefix="/api/v1/saude/usuarios", tags=["Saúde - Usuários"])
app.include_router(routes_saude.router, prefix="/api/v1/saude", tags=["Saúde - Dados"])
app.include_router(routes_dashboard_saude.router, prefix="/api/v1/saude", tags=["Saúde - Analytics"])



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


# Lista global para armazenar logs em memória (Buffer Circular)
from collections import deque
LOG_BUFFER = deque(maxlen=500)

class InMemoryHandler(logging.Handler):
    def emit(self, record):
        try:
            msg = self.format(record)
            LOG_BUFFER.append(msg)
        except Exception:
            self.handleError(record)

# Configurar logger para salvar no buffer também
memory_handler = InMemoryHandler()
memory_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
logging.getLogger().addHandler(memory_handler)

@app.get("/sistema/logs")
async def obter_logs(linhas: int = Query(50, ge=1, le=500)):
    """
    Rota para monitoramento técnico - lê do buffer em memória (Cloud Compatible)
    """
    try:
        # Pega as últimas N linhas do buffer
        # Convertendo para lista e pegando as últimas 'linhas'
        todos_logs = list(LOG_BUFFER)
        logs_recentes = todos_logs[-linhas:] if linhas < len(todos_logs) else todos_logs

        if not logs_recentes:
            logs_recentes = [f"Aguardando novos logs... (Buffer vazio)"]

        return {
            "servico": "eva-backend",
            "status": "online",
            "ambiente": "Cloud Run / Docker",
            "logs": logs_recentes
        }
    except Exception as e:
        return {"erro": f"Falha interna ao ler logs: {str(e)}"}


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