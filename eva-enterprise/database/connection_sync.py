from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()  # Carrega o .env

DATABASE_URL_SYNC = os.getenv("DATABASE_URL_SYNC")
if not DATABASE_URL_SYNC:
    raise ValueError("DATABASE_URL_SYNC não encontrada no .env")

engine = create_engine(DATABASE_URL_SYNC)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
