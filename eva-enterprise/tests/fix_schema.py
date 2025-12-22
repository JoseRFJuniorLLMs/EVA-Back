
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL não configurada!")

def add_column():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        try:
            print("Adicionando coluna 'observacao' na tabela 'sinais_vitais'...")
            conn.execute(text("ALTER TABLE sinais_vitais ADD COLUMN IF NOT EXISTS observacao TEXT;"))
            conn.commit()
            print("Coluna adicionada com sucesso!")
        except Exception as e:
            print(f"Erro: {e}")
            conn.rollback()

if __name__ == "__main__":
    add_column()
