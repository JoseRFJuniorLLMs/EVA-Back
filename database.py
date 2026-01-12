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


class Atendente(Base):
    __tablename__ = "atendentes"
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    status = Column(String, default="offline")  # online, offline, busy
    websocket_id = Column(String)
    last_seen = Column(DateTime, default=datetime.datetime.now)
    created_at = Column(DateTime, default=datetime.datetime.now)


class VideoCall(Base):
    __tablename__ = "video_calls"
    id = Column(Integer, primary_key=True)
    session_id = Column(String, unique=True, nullable=False)
    idoso_id = Column(Integer, ForeignKey('idosos.id'))
    atendente_id = Column(Integer, ForeignKey('atendentes.id'), nullable=True)
    status = Column(String, default="waiting")  # waiting, ringing, active, ended
    sdp_offer = Column(Text, nullable=True)
    sdp_answer = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.datetime.now)
    answered_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)


class AppLog(Base):
    __tablename__ = "app_logs"
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String)  # INFO, WARNING, ERROR, FATAL
    message = Column(Text)
    details = Column(Text)  # Stacktrace ou JSON extra
    device_info = Column(String)
    app_version = Column(String)
    user_cpf = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.now)


Base.metadata.create_all(bind=engine)