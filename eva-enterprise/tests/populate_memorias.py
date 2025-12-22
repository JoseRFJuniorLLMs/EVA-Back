
import os
import random
import sys
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, TIMESTAMP, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from faker import Faker
from dotenv import load_dotenv

# Ensure we can import from parent directory if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# --- Configuration ---
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL não configurada! Verifique seu arquivo .env")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
fake = Faker('pt_BR')

# --- Models ---

class Idoso(Base):
    __tablename__ = 'idosos'
    id = Column(Integer, primary_key=True)

class LegadoDigital(Base):
    __tablename__ = "idosos_legado_digital"
    
    id = Column(Integer, primary_key=True)
    idoso_id = Column(Integer, ForeignKey('idosos.id'))
    tipo = Column(String(50)) # 'audio', 'video', 'imagem', 'carta'
    titulo = Column(String(255))
    url_midia = Column(Text)
    destinatario = Column(String(255))
    protegido = Column(Boolean, default=True)
    criado_em = Column(TIMESTAMP, default=datetime.now)

# --- Data Generation ---

def populate_memorias():
    db = SessionLocal()
    print(f"Iniciando geração de 5 Memórias (Legado Digital) por Idoso em: {DATABASE_URL}")
    
    try:
        # Get all Idosos
        idosos_ids = db.query(Idoso.id).all()
        idosos_ids = [i[0] for i in idosos_ids]
        
        if not idosos_ids:
            print("Nenhum idoso encontrado.")
            return

        print(f"Encontrados {len(idosos_ids)} idosos. Gerando memórias...")
        
        count_created = 0
        
        for idoso_id in idosos_ids:
            for _ in range(5):
                tipo_memoria = random.choice(['audio', 'video', 'imagem', 'carta'])
                
                titulo = ""
                if tipo_memoria == 'audio':
                    titulo = f"Áudio sobre {fake.word()}"
                elif tipo_memoria == 'video':
                    titulo = f"Vídeo do {fake.word()}"
                elif tipo_memoria == 'imagem':
                    titulo = f"Foto em {fake.city()}"
                else:
                    titulo = f"Carta para {fake.first_name()}"

                memoria = LegadoDigital(
                    idoso_id=idoso_id,
                    tipo=tipo_memoria,
                    titulo=titulo,
                    url_midia=fake.url(),
                    destinatario="Família",
                    protegido=fake.boolean()
                )
                db.add(memoria)
                count_created += 1

        db.commit()
        print(f"Sucesso! {count_created} memórias criadas.")
        
    except Exception as e:
        print(f"Erro ao gerar memórias: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_memorias()
