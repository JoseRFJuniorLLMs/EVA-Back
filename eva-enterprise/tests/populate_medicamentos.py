
import os
import random
import sys
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, TIMESTAMP, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.types import JSON
from sqlalchemy.orm.attributes import flag_modified
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
    # Generic JSON for compatibility, though DB might be JSONB
    medicamentos_atuais = Column(JSON, default=[])

class Medicamento(Base):
    __tablename__ = 'medicamentos'
    
    id = Column(Integer, primary_key=True)
    idoso_id = Column(Integer, ForeignKey('idosos.id'))
    nome = Column(String(255), nullable=False)
    principio_ativo = Column(String(255))
    dosagem = Column(String(100))
    forma = Column(String(50))
    horarios = Column(JSON, default=[])
    observacoes = Column(Text)
    ativo = Column(Boolean, default=True)
    criado_em = Column(TIMESTAMP, default=datetime.now)
    atualizado_em = Column(TIMESTAMP, default=datetime.now)

# --- Data Generation ---

def populate_medicamentos():
    db = SessionLocal()
    print(f"Iniciando geração de 500 Medicamentos em: {DATABASE_URL}")
    
    try:
        # Get all Idosos
        idosos = db.query(Idoso).all()
        
        if not idosos:
            print("Nenhum idoso encontrado.")
            return

        print(f"Encontrados {len(idosos)} idosos. Gerando 500 medicamentos...")
        
        created_count = 0
        total_goal = 500
        
        # We'll use a local cache to update the JSON summary carefully
        # Initialize cache with current DB value (mostly empty if clean, or partial if populated)
        
        for _ in range(total_goal):
            idoso = random.choice(idosos)
            
            med_nome = fake.word().capitalize() + " " + str(random.choice([10, 20, 50, 100])) + "mg"
            
            med = Medicamento(
                idoso_id=idoso.id,
                nome=med_nome,
                principio_ativo=fake.word(),
                dosagem=str(random.choice([1, 2])) + " comprimido(s)",
                forma=random.choice(['comprimido', 'capsula', 'liquido']),
                horarios=[f"{random.randint(6,22):02d}:00"],
                observacoes=fake.sentence(),
                ativo=True
            )
            
            db.add(med)
            
            # Update Idoso JSON field
            # Ensure it's a list
            current_meds = list(idoso.medicamentos_atuais) if idoso.medicamentos_atuais else []
            current_meds.append(med_nome)
            idoso.medicamentos_atuais = current_meds
            
            # Explicitly flag modification for JSON fields in SQLAlchemy to ensure update
            flag_modified(idoso, "medicamentos_atuais")
            
            created_count += 1
            if created_count % 50 == 0:
                print(f"Gerados {created_count}...")

        db.commit()
        print(f"Sucesso! {created_count} medicamentos criados e perfis atualizados.")
        
    except Exception as e:
        print(f"Erro ao gerar medicamentos: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_medicamentos()
