from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

import os
from dotenv import load_dotenv

load_dotenv()

# Usa variável de ambiente ou fallback
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:Debian23%40@34.89.62.186:5432/eva")

# Ajusta string de conexão para garantir asyncpg
if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
    elif DATABASE_URL.startswith("postgresql://") and "+asyncpg" not in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Se for SQLite, garante o driver correto
if not DATABASE_URL or "sqlite" in DATABASE_URL:
    DATABASE_URL = "sqlite+aiosqlite:///./eva_saude.db"

print(f"🔌 Conectando ao banco de dados (ASYNC): {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'Local (SQLite)'}")

try:
    engine = create_async_engine(DATABASE_URL, echo=False)
except Exception as e:
    print(f"⚠️ Falha ao criar engine para {DATABASE_URL}: {e}")
    print("🔄 Tentando fallback para SQLite local...")
    DATABASE_URL = "sqlite+aiosqlite:///./eva_saude.db"
    engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
