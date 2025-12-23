import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from database.connection import Base
from database.models import * # Import all models to ensure they are registered
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Use SQLite if DB_URL is missing
    DATABASE_URL = "sqlite+aiosqlite:///./eva_saude.db"

if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

async def init_db():
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        print("Criando todas as tabelas...")
        await conn.run_sync(Base.metadata.create_all)
        print("Tabelas criadas com sucesso!")
        
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_db())
