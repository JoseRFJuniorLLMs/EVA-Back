"""
Synchronous Database Connection
===============================
Conexao sincrona com PostgreSQL para uso em tasks Celery.

Celery workers nao suportam async/await, entao usamos SQLAlchemy sincrono.
"""
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv

load_dotenv()

# URL sincrona (postgresql:// em vez de postgresql+asyncpg://)
DATABASE_URL_SYNC = os.getenv("DATABASE_URL_SYNC")

# Fallback: converter URL async para sync se necessario
if not DATABASE_URL_SYNC:
    async_url = os.getenv("DATABASE_URL", "")
    if async_url:
        DATABASE_URL_SYNC = async_url.replace("postgresql+asyncpg://", "postgresql://")
    else:
        raise ValueError("DATABASE_URL_SYNC ou DATABASE_URL não encontrada no .env")

# Engine com pool de conexoes
engine = create_engine(
    DATABASE_URL_SYNC,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verifica conexao antes de usar
    pool_recycle=3600,   # Recicla conexoes a cada 1h
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@contextmanager
def get_sync_db():
    """
    Context manager para obter sessao sincrona do banco.

    Uso:
        with get_sync_db() as db:
            result = db.execute(query)
            db.commit()
    """
    db: Session = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_sync_session() -> Session:
    """
    Retorna sessao sincrona (lembre de fechar manualmente).

    Uso:
        db = get_sync_session()
        try:
            result = db.execute(query)
            db.commit()
        finally:
            db.close()
    """
    return SessionLocal()
