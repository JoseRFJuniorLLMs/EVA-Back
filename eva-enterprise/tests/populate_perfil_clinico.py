
import os
import random
import sys
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, TIMESTAMP
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

class IdosoPerfilClinico(Base):
    __tablename__ = 'idosos_perfil_clinico'
    
    idoso_id = Column(Integer, ForeignKey('idosos.id'), primary_key=True)
    tipo_sanguineo = Column(String(5))
    alergias = Column(Text)
    restricoes_locomocao = Column(Text)
    doencas_cronicas = Column(Text)
    atualizado_em = Column(TIMESTAMP, default=datetime.now)

# --- Data Generation ---

def populate_perfil_clinico():
    db = SessionLocal()
    print(f"Iniciando geração de Perfil Clínico em: {DATABASE_URL}")
    
    try:
        # Get all Idosos IDs
        idosos_ids = db.query(Idoso.id).all()
        idosos_ids = [i[0] for i in idosos_ids]
        
        if not idosos_ids:
            print("Nenhum idoso encontrado.")
            return

        print(f"Encontrados {len(idosos_ids)} idosos. Verificando perfis existentes...")
        
        count_created = 0
        for idoso_id in idosos_ids:
            # Check if profile exists
            exists = db.query(IdosoPerfilClinico).filter_by(idoso_id=idoso_id).first()
            if exists:
                continue

            perfil = IdosoPerfilClinico(
                idoso_id=idoso_id,
                tipo_sanguineo=random.choice(['A+', 'A-', 'B+', 'O+', 'O-', 'AB+']),
                alergias=fake.words(nb=3, ext_word_list=['Penicilina', 'Dipirona', 'Poeira', 'Amendoim', 'Nenhuma', 'Sulfa', 'Lactose']),
                restricoes_locomocao=fake.sentence() if random.choice([True, False]) else None,
                doencas_cronicas=fake.sentence()
            )
            
            # Convert list to string for text fields if needed, but fake.words return list
            if isinstance(perfil.alergias, list):
                 perfil.alergias = ", ".join(perfil.alergias)

            db.add(perfil)
            count_created += 1

        db.commit()
        print(f"Sucesso! {count_created} perfis clínicos criados.")
        
    except Exception as e:
        print(f"Erro ao gerar perfis clínicos: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_perfil_clinico()
