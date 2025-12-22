
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Ensure we can import from parent directory if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL não configurada!")

def verify_counts():
    engine = create_engine(DATABASE_URL)
    tables = [
        "idosos",
        "membros_familia",
        "medicamentos",
        "agendamentos",
        "idosos_perfil_clinico",
        "idosos_legado_digital",
        "sinais_vitais"
    ]
    
    print(f"--- Verificando contagens no banco: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else '...'} ---")
    
    with engine.connect() as conn:
        for table in tables:
            try:
                result = conn.execute(text(f"SELECT count(*) FROM {table}"))
                count = result.scalar()
                print(f"{table}: {count}")
            except Exception as e:
                print(f"{table}: ERRO ({e})")

if __name__ == "__main__":
    verify_counts()
