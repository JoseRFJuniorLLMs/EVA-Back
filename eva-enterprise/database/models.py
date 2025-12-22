from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
import datetime
from .connection import Base

class Idoso(Base):
    __tablename__ = "idosos"
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    data_nascimento = Column(String)  # DATE in SQL, using String for SQLite compatibility
    telefone = Column(String, nullable=False)
    cpf = Column(String, unique=True)  # CPF brasileiro (formato: 000.000.000-00 ou 00000000000)
    foto_url = Column(Text)
    intro_audio_url = Column(Text)
    
    # Perfil de Saúde
    nivel_cognitivo = Column(String, default='normal')
    limitacoes_auditivas = Column(Boolean, default=False)
    usa_aparelho_auditivo = Column(Boolean, default=False)
    limitacoes_visuais = Column(Boolean, default=False)
    mobilidade = Column(String, default='independente')
    
    # Personalização
    tom_voz = Column(String, default='amigavel')
    preferencia_horario_ligacao = Column(String, default='manha')
    timezone = Column(String, default='America/Sao_Paulo')
    
    # Ajustes Técnicos de Áudio
    ganho_audio_entrada = Column(Integer, default=0)
    ganho_audio_saida = Column(Integer, default=0)
    ambiente_ruidoso = Column(Boolean, default=False)
    
    # Contatos de Emergência (JSONB in PostgreSQL, JSON in SQLite)
    familiar_principal = Column(JSON, default={})
    contato_emergencia = Column(JSON, default={})
    medico_responsavel = Column(JSON, default={})
    
    # Dados médicos
    medicamentos_atuais = Column(JSON, default=[])
    condicoes_medicas = Column(Text)
    
    # Estado Emocional e Tracking
    sentimento = Column(String, default='neutro')
    agendamentos_pendentes = Column(Integer, default=0)
    
    # Campos legados (manter compatibilidade)
    endereco = Column(String)
    medicamentos_regulares = Column(Text)
    
    # Metadata
    notas_gerais = Column(Text)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.datetime.now)
    atualizado_em = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    # Relacionamento com agendamentos
    agendamentos = relationship("Agendamento", back_populates="idoso")
    medicamentos = relationship("Medicamento", back_populates="idoso")
    historico = relationship("Historico", back_populates="idoso")
    familiares = relationship("Familiar", back_populates="idoso")
    legado_digital = relationship("LegadoDigital", back_populates="idoso")
    sinais_vitais = relationship("SinaisVitais", back_populates="idoso")
    insights_psicologia = relationship("PsicologiaInsight", back_populates="idoso")
    topicos_afetivos = relationship("TopicoAfetivo", back_populates="idoso")



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
    idoso_id = Column(Integer, ForeignKey('idosos.id'))
    criado_em = Column(DateTime, default=datetime.datetime.now)

    idoso = relationship("Idoso", back_populates="familiares")


class LegadoDigital(Base):
    __tablename__ = "idosos_legado_digital"
    id = Column(Integer, primary_key=True)
    idoso_id = Column(Integer, ForeignKey('idosos.id'))
    titulo = Column(String)
    tipo_midia = Column(String) # audio, video, text
    url_arquivo = Column(String)
    descricao = Column(Text)
    criado_em = Column(DateTime, default=datetime.datetime.now)

    idoso = relationship("Idoso", back_populates="legado_digital")


class SinaisVitais(Base):
    __tablename__ = "sinais_vitais"
    id = Column(Integer, primary_key=True)
    idoso_id = Column(Integer, ForeignKey('idosos.id'))
    tipo = Column(String) # pressao, glicose, peso, batimentos
    valor = Column(String)
    unidade = Column(String)
    data_medicao = Column(DateTime, default=datetime.datetime.now)
    observacao = Column(Text)

    idoso = relationship("Idoso", back_populates="sinais_vitais")


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


class PsicologiaInsight(Base):
    __tablename__ = "psicologia_insights"
    id = Column(Integer, primary_key=True)
    idoso_id = Column(Integer, ForeignKey('idosos.id'))
    conteudo = Column(Text)
    data_geracao = Column(DateTime, default=datetime.datetime.now)
    relevancia = Column(Integer, default=0) # 0-10

    idoso = relationship("Idoso", back_populates="insights_psicologia")


class TopicoAfetivo(Base):
    __tablename__ = "topicos_afetivos"
    id = Column(Integer, primary_key=True)
    idoso_id = Column(Integer, ForeignKey('idosos.id'))
    topico = Column(String)
    frequencia = Column(Integer, default=1)
    ultima_mencao = Column(DateTime, default=datetime.datetime.now)

    idoso = relationship("Idoso", back_populates="topicos_afetivos")


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
    __tablename__ = "configuracoes_sistema"
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

class CircuitBreakerState(Base):
    __tablename__ = "circuit_breaker_states"
    id = Column(Integer, primary_key=True)
    service_name = Column(String, unique=True)
    state = Column(String, default="closed") # closed, open, half-open
    failure_count = Column(Integer, default=0)
    last_failure_time = Column(DateTime, nullable=True)

class RateLimit(Base):
    __tablename__ = "rate_limits"
    id = Column(Integer, primary_key=True)
    endpoint = Column(String, unique=True)
    limit_count = Column(Integer, default=100)
    interval_seconds = Column(Integer, default=60)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    acao = Column(String)
    usuario = Column(String)
    detalhes = Column(JSON)
    data = Column(DateTime, default=datetime.datetime.now)
