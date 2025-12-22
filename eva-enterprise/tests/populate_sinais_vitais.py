
import os
import random
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime
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

class SinaisVitais(Base):
    __tablename__ = "sinais_vitais"
    
    id = Column(Integer, primary_key=True)
    idoso_id = Column(Integer, ForeignKey('idosos.id'))
    tipo = Column(String) # pressao, glicose, peso, batimentos
    valor = Column(String)
    unidade = Column(String)
    data_medicao = Column(DateTime, default=datetime.now)
    observacao = Column(Text)

# --- Data Generation ---

def generate_vital_sign(tipo):
    if tipo == 'batimentos':
        val = random.randint(60, 100)
        return str(val), 'bpm'
    elif tipo == 'pressao':
        sistolica = random.randint(110, 140)
        diastolica = random.randint(70, 90)
        return f"{sistolica}/{diastolica}", 'mmHg'
    elif tipo == 'glicose':
        val = random.randint(70, 140)
        return str(val), 'mg/dL'
    elif tipo == 'peso':
        val = round(random.uniform(50.0, 90.0), 1)
        return str(val), 'kg'
    return "0", ""

def populate_sinais_vitais():
    db = SessionLocal()
    print(f"Iniciando geração de Sinais Vitais (1 semana) em: {DATABASE_URL}")
    
    try:
        # Get all Idosos
        idosos_ids = db.query(Idoso.id).all()
        idosos_ids = [i[0] for i in idosos_ids]
        
        if not idosos_ids:
            print("Nenhum idoso encontrado.")
            return

        print(f"Encontrados {len(idosos_ids)} idosos. Gerando histórico de 1 semana...")
        
        count_created = 0
        now = datetime.now()
        
        for idoso_id in idosos_ids:
            # Generate for last 7 days
            for d in range(7):
                current_date = now - timedelta(days=d)
                
                # 1. Batimentos (3x: Manhã, Tarde, Noite)
                for hour in [8, 14, 20]:
                    # Randomize time slightly +/- 30 mins
                    mins = random.randint(-30, 30)
                    med_time = current_date.replace(hour=hour, minute=0, second=0) + timedelta(minutes=mins)
                    
                    val, unit = generate_vital_sign('batimentos')
                    sinal = SinaisVitais(
                        idoso_id=idoso_id,
                        tipo='batimentos',
                        valor=val,
                        unidade=unit,
                        data_medicao=med_time,
                        observacao="Medição de rotina"
                    )
                    db.add(sinal)
                    count_created += 1
                
                # 2. Pressão (2x: Manhã, Noite)
                for hour in [9, 21]:
                    mins = random.randint(-30, 30)
                    med_time = current_date.replace(hour=hour, minute=0, second=0) + timedelta(minutes=mins)
                    
                    val, unit = generate_vital_sign('pressao')
                    sinal = SinaisVitais(
                        idoso_id=idoso_id,
                        tipo='pressao',
                        valor=val,
                        unidade=unit,
                        data_medicao=med_time
                    )
                    db.add(sinal)
                    count_created += 1

                # 3. Glicose (1x: Manhã jejum)
                med_time = current_date.replace(hour=7, minute=30, second=0) + timedelta(minutes=random.randint(0, 30))
                val, unit = generate_vital_sign('glicose')
                sinal_glicose = SinaisVitais(
                    idoso_id=idoso_id,
                    tipo='glicose',
                    valor=val,
                    unidade=unit,
                    data_medicao=med_time,
                    observacao="Jejum"
                )
                db.add(sinal_glicose)
                count_created += 1
            
            # 4. Peso (1x na semana)
            # Pick a random day in the week
            rand_day = random.randint(0, 6)
            med_time = (now - timedelta(days=rand_day)).replace(hour=10, minute=0)
            val, unit = generate_vital_sign('peso')
            sinal_peso = SinaisVitais(
                idoso_id=idoso_id,
                tipo='peso',
                valor=val,
                unidade=unit,
                data_medicao=med_time
            )
            db.add(sinal_peso)
            count_created += 1

        db.commit()
        print(f"Sucesso! {count_created} registros de sinais vitais criados.")
        
    except Exception as e:
        print(f"Erro ao gerar sinais vitais: {e}")
        db.rollback()
    finally:
        db.close()

def check_schema():
    """Ensure the schema has the required columns."""
    from sqlalchemy import text
    try:
        with engine.connect() as conn:
            # Check if column exists
            result = conn.execute(text(
                "SELECT column_name FROM information_schema.columns WHERE table_name='sinais_vitais' AND column_name='observacao'"
            ))
            if not result.fetchone():
                print("Coluna 'observacao' não encontrada. Adicionando...")
                conn.execute(text("ALTER TABLE sinais_vitais ADD COLUMN IF NOT EXISTS observacao TEXT"))
                conn.commit()
                print("Schema atualizado com sucesso.")
            else:
                print("Schema verificado: Coluna 'observacao' já existe.")
    except Exception as e:
        print(f"Aviso ao verificar schema: {e}")

if __name__ == "__main__":
    check_schema()
    populate_sinais_vitais()
