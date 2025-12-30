from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

import os
from dotenv import load_dotenv

from pathlib import Path
env_path = Path(__file__).parent.parent / '.env'
print(f"📖 Tentando carregar .env de: {env_path}")
print(f"Arquivo existe? {env_path.exists()}")
load_dotenv(dotenv_path=env_path)

# Prioridade: 1. ASYNC, 2. DATABASE_URL (legado), 3. SYNC (fallback com conversão)
DATABASE_URL = os.getenv("DATABASE_URL_ASYNC")

if not DATABASE_URL:
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL:
        print("ℹ️ Usando DATABASE_URL (legado)")

if not DATABASE_URL:
    DATABASE_URL_SYNC = os.getenv("DATABASE_URL_SYNC")
    if DATABASE_URL_SYNC:
        print("ℹ️ Usando DATABASE_URL_SYNC como fallback para ASYNC")
        DATABASE_URL = DATABASE_URL_SYNC

if not DATABASE_URL:
    print("❌ ERRO CRÍTICO: Nenhuma DATABASE_URL (ASYNC, SYNC ou padrão) encontrada no .env")
    # Listar chaves disponíveis para debug (sem valores)
    print(f"Chaves no ambiente: {[k for k in os.environ.keys() if 'DB' in k or 'URL' in k]}")
    # Opcional: Levantar exceção para impedir fallback silencioso se for requisito estrito
    # raise ValueError("DATABASE_URL is required in .env")

# Ajusta string de conexão para garantir asyncpg
if DATABASE_URL:
    if "postgresql+asyncpg" not in DATABASE_URL:
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
        elif DATABASE_URL.startswith("postgresql://"):
            DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif "://" in DATABASE_URL and (DATABASE_URL.startswith("postgresql+") or "postgres" in DATABASE_URL.split("://")[0]):
            # Trata casos como postgresql+psycopg2://
            prefix = DATABASE_URL.split("://")[0]
            DATABASE_URL = DATABASE_URL.replace(prefix, "postgresql+asyncpg", 1)

# Se for SQLite, garante o driver correto
if DATABASE_URL and "sqlite" in DATABASE_URL:
     pass # Mantém como está se for explicitamente sqlite

if not DATABASE_URL:
    raise ValueError("❌ ERRO: DATABASE_URL (ou DATABASE_URL_SYNC) obrigatória não encontrada no .env para conexão PostgreSQL.")

print(f"🔌 Conectando ao banco de dados (ASYNC): {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'Local (SQLite)'}")

try:
    engine = create_async_engine(DATABASE_URL, echo=False)
except Exception as e:
    print(f"⚠️ Falha ao criar engine para {DATABASE_URL}: {e}")
    raise e
    
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
