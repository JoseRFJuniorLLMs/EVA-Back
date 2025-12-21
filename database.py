from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

DATABASE_URL = "sqlite:///./eva_saude.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Idoso(Base):
    __tablename__ = "idosos"
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    telefone = Column(String, nullable=False)
    endereco = Column(String)
    condicoes_medicas = Column(Text)
    medicamentos_regulares = Column(Text)
    criado_em = Column(DateTime, default=datetime.datetime.now)

    # Relacionamento com agendamentos
    agendamentos = relationship("Agendamento", back_populates="idoso")


class Familiar(Base):
    __tablename__ = "familiares"
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    parentesco = Column(String)
    telefone = Column(String, nullable=False)
    email = Column(String)
    eh_responsavel = Column(Boolean, default=False)
    criado_em = Column(DateTime, default=datetime.datetime.now)


class Agendamento(Base):
    __tablename__ = "agendamentos"
    id = Column(Integer, primary_key=True)
    idoso_id = Column(Integer, ForeignKey('idosos.id'))
    telefone = Column(String)
    nome_idoso = Column(String)
    horario = Column(DateTime)
    remedios = Column(Text)
    status = Column(String, default="pendente")  # pendente, ligado, concluido, nao_atendeu

    # Relacionamento com idoso
    idoso = relationship("Idoso", back_populates="agendamentos")


class Alerta(Base):
    __tablename__ = "alertas"
    id = Column(Integer, primary_key=True)
    tipo = Column(String)  # "NAO_ATENDEU" ou "PASSA_MAL" ou "ERRO_SISTEMA"
    descricao = Column(Text)
    criado_em = Column(DateTime, default=datetime.datetime.now)


Base.metadata.create_all(bind=engine)