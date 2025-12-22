
import os
import random
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean, Text, ForeignKey, TIMESTAMP, Numeric
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON
from faker import Faker

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL não configurada! Verifique seu arquivo .env")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
fake = Faker('pt_BR')

# --- Models (Matching eva-v7.sql) ---

class Idoso(Base):
    __tablename__ = 'idosos'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(255), nullable=False)
    data_nascimento = Column(Date, nullable=False)
    telefone = Column(String(20), nullable=False)
    cpf = Column(String(14), unique=True)
    foto_url = Column(Text)
    intro_audio_url = Column(Text)
    
    # Perfil de Saúde
    nivel_cognitivo = Column(String(50), default='normal')
    limitacoes_auditivas = Column(Boolean, default=False)
    usa_aparelho_auditivo = Column(Boolean, default=False)
    limitacoes_visuais = Column(Boolean, default=False)
    mobilidade = Column(String(50), default='independente')
    
    # Personalização
    tom_voz = Column(String(50), default='amigavel')
    preferencia_horario_ligacao = Column(String(50), default='manha')
    timezone = Column(String(50), default='America/Sao_Paulo')
    
    # Ajustes Técnicos
    ganho_audio_entrada = Column(Integer, default=0)
    ganho_audio_saida = Column(Integer, default=0)
    ambiente_ruidoso = Column(Boolean, default=False)
    
    # JSON fields - Using generic JSON for broader compatibility, but eva-v7 uses JSONB
    familiar_principal = Column(JSON, default={"nome": "", "telefone": "", "parentesco": ""})
    contato_emergencia = Column(JSON, default={"nome": "", "telefone": "", "parentesco": ""})
    medico_responsavel = Column(JSON, default={"nome": "", "telefone": "", "crm": ""})
    
    medicamentos_atuais = Column(JSON, default=[])
    condicoes_medicas = Column(Text)
    
    sentimento = Column(String(50), default='neutro')
    agendamentos_pendentes = Column(Integer, default=0)
    
    notas_gerais = Column(Text)
    ativo = Column(Boolean, default=True)
    criado_em = Column(TIMESTAMP, default=datetime.now)
    atualizado_em = Column(TIMESTAMP, default=datetime.now)

class MembroFamilia(Base):
    __tablename__ = 'membros_familia'
    
    id = Column(Integer, primary_key=True)
    idoso_id = Column(Integer, ForeignKey('idosos.id'))
    parent_id = Column(Integer, ForeignKey('membros_familia.id'), nullable=True)
    nome = Column(String(255), nullable=False)
    parentesco = Column(String(100), nullable=False)
    foto_url = Column(Text)
    is_responsavel = Column(Boolean, default=False)
    telefone = Column(String(20))
    criado_em = Column(TIMESTAMP, default=datetime.now)
    atualizado_em = Column(TIMESTAMP, default=datetime.now)

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

class IdosoPerfilClinico(Base):
    __tablename__ = 'idosos_perfil_clinico'
    
    idoso_id = Column(Integer, ForeignKey('idosos.id'), primary_key=True)
    tipo_sanguineo = Column(String(5))
    alergias = Column(Text)
    restricoes_locomocao = Column(Text)
    doencas_cronicas = Column(Text)
    atualizado_em = Column(TIMESTAMP, default=datetime.now)


# --- Validators / Helpers ---
def generate_cpf():
    return fake.cpf()

def generate_phone():
    return fake.cellphone_number()

# --- Data Generation ---

def populate_database(num_records=100):
    db = SessionLocal()
    print(f"Iniciando geração de {num_records} registros...")
    
    try:
        # Create tables if they verify_tables_exist (Optional, usually schema is already there)
        # Base.metadata.create_all(engine) 
        
        for _ in range(num_records):
            # 1. Idoso
            sexo = random.choice(['M', 'F'])
            if sexo == 'M':
                nome = fake.name_male()
            else:
                nome = fake.name_female()
            
            data_nascimento = fake.date_of_birth(minimum_age=65, maximum_age=95)
            
            idoso = Idoso(
                nome=nome,
                data_nascimento=data_nascimento,
                telefone=generate_phone(),
                cpf=generate_cpf(),
                foto_url=fake.image_url(),
                intro_audio_url=fake.url(),
                nivel_cognitivo=random.choice(['normal', 'leve', 'moderado', 'severo']),
                limitacoes_auditivas=fake.boolean(chance_of_getting_true=30),
                usa_aparelho_auditivo=fake.boolean(chance_of_getting_true=20),
                limitacoes_visuais=fake.boolean(chance_of_getting_true=25),
                mobilidade=random.choice(['independente', 'auxiliado', 'cadeira_rodas', 'acamado']),
                tom_voz=random.choice(['formal', 'amigavel', 'maternal', 'jovial']),
                preferencia_horario_ligacao=random.choice(['manha', 'tarde', 'noite', 'qualquer']),
                medicamentos_atuais=[], # Will be populated implicitly via relationship/logic if needed, but here simple
                condicoes_medicas=fake.sentence(),
                notas_gerais=fake.text(),
                sentimento=random.choice(['feliz', 'neutro', 'triste', 'ansioso']),
            )
            
            db.add(idoso)
            db.flush() # Get ID
            
            # 2. Perfil Clinico
            perfil = IdosoPerfilClinico(
                idoso_id=idoso.id,
                tipo_sanguineo=random.choice(['A+', 'A-', 'B+', 'O+', 'O-', 'AB+']),
                alergias=fake.words(nb=3, ext_word_list=['Penicilina', 'Dipirona', 'Poeira', 'Amendoim', 'Nenhuma']),
                restricoes_locomocao=fake.sentence() if idoso.mobilidade != 'independente' else None,
                doencas_cronicas=fake.sentence()
            )
            db.add(perfil)
            
            # 3. Membros Familia (1 a 3)
            num_familiares = random.randint(1, 3)
            tem_responsavel = False
            
            for i in range(num_familiares):
                is_resp = False
                if not tem_responsavel and i == num_familiares - 1:
                    is_resp = True
                elif not tem_responsavel:
                    is_resp = fake.boolean(chance_of_getting_true=50)
                    if is_resp: tem_responsavel = True
                
                familiar = MembroFamilia(
                    idoso_id=idoso.id,
                    nome=fake.name(),
                    parentesco=random.choice(['Filho(a)', 'Neto(a)', 'Sobrinho(a)', 'Irmão(ã)']),
                    telefone=generate_phone(),
                    foto_url=fake.image_url(),
                    is_responsavel=is_resp
                )
                db.add(familiar)
                
                # Update familiar_principal in idoso if responsavel
                if is_resp:
                    idoso.familiar_principal = {
                        "nome": familiar.nome,
                        "telefone": familiar.telefone,
                        "parentesco": familiar.parentesco
                    }
                    idoso.contato_emergencia = {
                         "nome": familiar.nome,
                         "telefone": familiar.telefone,
                         "parentesco": familiar.parentesco
                    }

            # 4. Medicamentos (0 a 5)
            num_meds = random.randint(0, 5)
            med_list_names = []
            for _ in range(num_meds):
                med_nome = fake.word().capitalize() + " " + str(random.choice([10, 20, 50, 100])) + "mg"
                med = Medicamento(
                    idoso_id=idoso.id,
                    nome=med_nome,
                    principio_ativo=fake.word(),
                    dosagem=str(random.choice([1, 2])) + " comprimido(s)",
                    forma=random.choice(['comprimido', 'capsula', 'liquido']),
                    horarios=[f"{random.randint(6,22):02d}:00"],
                    observacoes=fake.sentence()
                )
                db.add(med)
                med_list_names.append(med_nome)
            
            # Update idoso json summary
            idoso.medicamentos_atuais = med_list_names

        db.commit()
        print("Dados gerados com sucesso!")
        
    except Exception as e:
        print(f"Erro ao popular banco dados: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_database(100)
