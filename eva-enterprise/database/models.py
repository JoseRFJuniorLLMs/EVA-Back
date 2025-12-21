from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
import datetime
from .connection import Base

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
    medicamentos = relationship("Medicamento", back_populates="idoso")


class Medicamento(Base):
    __tablename__ = "medicamentos"
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    dosagem = Column(String)
    horarios = Column(JSON)  # Store list of times like ["08:00", "20:00"]
    idoso_id = Column(Integer, ForeignKey('idosos.id'))
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.datetime.now)

    idoso = relationship("Idoso", back_populates="medicamentos")


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
