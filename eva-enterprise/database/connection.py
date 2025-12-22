from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os
from dotenv import load_dotenv

load_dotenv()

# Usa variável de ambiente ou fallback (apenas se não houver env)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./eva_saude.db")

# Ajusta string de conexão se for Postgres
if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    if "+asyncpg" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("+asyncpg", "", 1)

print(f"🔌 Conectando ao banco de dados: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'SQLite/Local'}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
