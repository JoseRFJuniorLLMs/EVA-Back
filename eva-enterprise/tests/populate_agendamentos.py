
import os
import random
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean, Text, ForeignKey, TIMESTAMP
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.types import JSON
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

# --- Models (Minimal for FK references) ---

class Idoso(Base):
    __tablename__ = 'idosos'
    id = Column(Integer, primary_key=True)

class Agendamento(Base):
    __tablename__ = 'agendamentos'
    
    id = Column(Integer, primary_key=True)
    idoso_id = Column(Integer, ForeignKey('idosos.id'))
    tipo = Column(String(50), nullable=False) # 'lembrete_medicamento', 'check_bem_estar', 'acompanhamento_pos_consulta', 'atividade_fisica'
    
    # Scheduling
    data_hora_agendada = Column(TIMESTAMP, nullable=False)
    data_hora_realizada = Column(TIMESTAMP)
    
    # Retry Policy
    max_retries = Column(Integer, default=3)
    retry_interval_minutes = Column(Integer, default=15)
    tentativas_realizadas = Column(Integer, default=0)
    proxima_tentativa = Column(TIMESTAMP)
    escalation_policy = Column(String(50), default='alert_family')
    
    # Estado da Ligação
    status = Column(String(50), default='agendado')
    
    # Session Management
    gemini_session_handle = Column(String(255))
    ultima_interacao_estado = Column(JSON)
    session_expires_at = Column(TIMESTAMP)
    
    # Dados Tarefa
    dados_tarefa = Column(JSON, default={})
    prioridade = Column(String(10), default='normal')
    
    # Metadata
    criado_por = Column(String(100), default='script_populacao')
    criado_em = Column(TIMESTAMP, default=datetime.now)
    atualizado_em = Column(TIMESTAMP, default=datetime.now)

# --- Data Generation ---

def populate_agendamentos():
    db = SessionLocal()
    print(f"Iniciando geração de Agendamentos em: {DATABASE_URL}")
    
    try:
        # Get all Idosos IDs
        idosos_ids = db.query(Idoso.id).all()
        idosos_ids = [i[0] for i in idosos_ids]
        
        if not idosos_ids:
            print("Nenhum idoso encontrado. Rode o script populate_db.py primeiro.")
            return

        print(f"Encontrados {len(idosos_ids)} idosos. Gerando agendamentos...")
        
        for idoso_id in idosos_ids:
            # 1. Create 1 Agendamento per Idoso
            
            tipo_agendamento = random.choice(['lembrete_medicamento', 'check_bem_estar', 'acompanhamento_pos_consulta', 'atividade_fisica'])
            
            # Random date in the next 7 days
            days_ahead = random.randint(0, 7)
            hour = random.randint(8, 20)
            minutes = random.choice([0, 15, 30, 45])
            
            data_agendada = datetime.now() + timedelta(days=days_ahead)
            data_agendada = data_agendada.replace(hour=hour, minute=minutes, second=0, microsecond=0)
            
            # Dados Tarefa Mock
            dados_tarefa = {}
            if tipo_agendamento == 'lembrete_medicamento':
                dados_tarefa = {
                    "medicamento": fake.word().capitalize() + " 50mg",
                    "dosagem": "1 comprimido"
                }
            elif tipo_agendamento == 'check_bem_estar':
                dados_tarefa = {
                    "contexto": "Monitoramento de rotina"
                }

            agendamento = Agendamento(
                idoso_id=idoso_id,
                tipo=tipo_agendamento,
                data_hora_agendada=data_agendada,
                status='agendado',
                dados_tarefa=dados_tarefa,
                prioridade=random.choice(['normal', 'alta', 'baixa']),
                criado_por='script_populacao'
            )
            
            db.add(agendamento)

        db.commit()
        print(f"Sucesso! {len(idosos_ids)} agendamentos criados.")
        
    except Exception as e:
        print(f"Erro ao gerar agendamentos: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_agendamentos()
