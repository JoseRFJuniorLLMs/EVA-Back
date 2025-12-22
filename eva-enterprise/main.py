import uvicorn
from fastapi import FastAPI
from database.connection import engine, Base
from config.settings import settings

# Imports from api package
from api.routes_alertas import router as alertas_router
from api.routes_config import router as config_router
from api.routes_extras import router as extras_router
from api.routes_idosos import router as idosos_router
from api.routes_medicamentos import router as medicamentos_router
from api.routes_pagamentos import router as pagamentos_router
from api.webhooks import router as webhooks_router
from api.calls import router as calls_router
from api.routes_agendamentos import router as agendamentos_router
from api.routes_orquestrador import router as orquestrador_router

# Create Database Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="EVA Enterprise API",
    description="API set for Eva Enterprise",
    version="6.0"
)

# Inclui todos os routers
app.include_router(alertas_router, prefix="/alertas", tags=["Alertas e Insights"])
app.include_router(config_router, prefix="/configs", tags=["Configurações"])
app.include_router(extras_router, prefix="/extras", tags=["Extras e Relatórios"])
app.include_router(orquestrador_router, prefix="/orquestrador", tags=["Orquestrador de Fluxos"])
app.include_router(idosos_router, prefix="/idosos", tags=["Idosos e Familiares"])
app.include_router(medicamentos_router, prefix="/medicamentos", tags=["Medicamentos e Sinais Vitais"])
app.include_router(pagamentos_router, prefix="/pagamentos", tags=["Pagamentos e Auditoria"])
app.include_router(webhooks_router, tags=["Webhooks"])
app.include_router(calls_router, tags=["Chamadas"])
app.include_router(agendamentos_router, prefix="/agendamentos", tags=["Agendamentos e Histórico"])

@app.get("/")
def root():
    return {"message": "Eva Enterprise Running 🚀"}

# Inicia o scheduler automático quando roda diretamente
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 EVA ENTERPRISE - Assistente de Voz")
    print("=" * 60)
    print(f"Porta: {settings.PORT}")
    print(f"Domínio: {settings.SERVICE_DOMAIN}")
    print("=" * 60 + "\n")

    # Importa e inicia o scheduler
    from scheduler import iniciar_scheduler

    iniciar_scheduler()

    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
