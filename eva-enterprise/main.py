import uvicorn
from fastapi import FastAPI
from database.connection import engine, Base
from config.settings import settings
from api import calls, webhooks

# Create Database Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Eva Enterprise", description="Assistente Virtual para Idosos")

# Include Routers
app.include_router(calls.router)
app.include_router(webhooks.router)


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