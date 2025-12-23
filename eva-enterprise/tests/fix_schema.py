import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL não configurada!")

# Converte URL para asyncpg se necessário
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

async def add_column():
    engine = create_async_engine(DATABASE_URL)
    async with engine.connect() as conn:
        try:
            print("Adicionando coluna 'observacao' na tabela 'sinais_vitais'...")
            await conn.execute(text("ALTER TABLE sinais_vitais ADD COLUMN IF NOT EXISTS observacao TEXT;"))
            await conn.commit()
            print("Coluna adicionada com sucesso!")
        except Exception as e:
            print(f"Erro: {e}")
            await conn.rollback()
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(add_column())
