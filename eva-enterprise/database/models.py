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
    historico = relationship("Historico", back_populates="idoso")


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
    tentativas_realizadas = Column(Integer, default=0)
    proxima_tentativa = Column(DateTime, nullable=True)

    # Relacionamento com idoso
    idoso = relationship("Idoso", back_populates="agendamentos")


class Alerta(Base):
    __tablename__ = "alertas"
    id = Column(Integer, primary_key=True)
    tipo = Column(String)  # "NAO_ATENDEU" ou "PASSA_MAL" ou "ERRO_SISTEMA"
    descricao = Column(Text)
    status = Column(String, default="ativo") # ativo, resolvido
    criado_em = Column(DateTime, default=datetime.datetime.now)


class Historico(Base):
    __tablename__ = "historico"
    id = Column(Integer, primary_key=True)
    agendamento_id = Column(Integer, ForeignKey('agendamentos.id'), nullable=True)
    idoso_id = Column(Integer, ForeignKey('idosos.id'), nullable=True)
    call_sid = Column(String, nullable=True)
    evento = Column(String, default="Ligação Realizada") # Ligação, Medicamento Confirmado, etc
    status = Column(String) # sucesso, falha, alerta
    detalhe = Column(Text, nullable=True)
    sentimento = Column(String, nullable=True) # feliz, neutro, ansioso
    inicio = Column(DateTime, nullable=True)
    fim = Column(DateTime, nullable=True)
    criado_em = Column(DateTime, default=datetime.datetime.now)

    idoso = relationship("Idoso", back_populates="historico")


class Pagamento(Base):
    __tablename__ = "pagamentos"
    id = Column(Integer, primary_key=True)
    descricao = Column(String)
    valor = Column(Integer) # em centavos ou float? Vamos assumir float por simplicidade ou decimal
    metodo = Column(String) # Cartão, PIX
    status = Column(String) # pago, pendente
    data = Column(DateTime, default=datetime.datetime.now)


# --- Enterprise Settings ---

class Configuracao(Base):
    __tablename__ = "configuracoes"
    id = Column(Integer, primary_key=True)
    chave = Column(String, unique=True, nullable=False)
    valor = Column(String)
    tipo = Column(String) # text, number, boolean, json
    categoria = Column(String) # system, llm, voice, limits

class Prompt(Base):
    __tablename__ = "prompts"
    id = Column(Integer, primary_key=True)
    nome = Column(String, unique=True)
    template = Column(Text)
    versao = Column(String)
    ativo = Column(Boolean, default=True)

class Funcao(Base):
    __tablename__ = "funcoes"
    id = Column(Integer, primary_key=True)
    nome = Column(String, unique=True)
    descricao = Column(String)
    parameters = Column(JSON) # JSON Schema
    tipo_tarefa = Column(String) # data_retrieval, action, etc

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    acao = Column(String)
    usuario = Column(String)
    detalhes = Column(JSON)
    data = Column(DateTime, default=datetime.datetime.now)
