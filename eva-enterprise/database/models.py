from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON, Date, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
import datetime
from .connection import Base

class Idoso(Base):
    __tablename__ = "idosos"
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    data_nascimento = Column(Date, nullable=False)
    telefone = Column(String, nullable=False)
    cpf = Column(String, unique=True)
    foto_url = Column(Text)
    intro_audio_url = Column(Text)
    device_token = Column(Text, nullable=True)  # 26/12/2015 update para tokern firebase
    
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
    
    # Contatos de Emergência
    familiar_principal = Column(JSON, default={"nome": "", "telefone": "", "parentesco": ""})
    contato_emergencia = Column(JSON, default={"nome": "", "telefone": "", "parentesco": ""})
    medico_responsavel = Column(JSON, default={"nome": "", "telefone": "", "crm": ""})
    
    # Dados médicos
    medicamentos_atuais = Column(JSON, default=[])
    condicoes_medicas = Column(Text)
    
    # Estado Emocional e Tracking
    sentimento = Column(String, default='neutro')
    agendamentos_pendentes = Column(Integer, default=0)
    
    # Metadata
    notas_gerais = Column(Text)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.datetime.now)
    atualizado_em = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    # Relacionamentos
    agendamentos = relationship("Agendamento", back_populates="idoso")
    medicamentos = relationship("Medicamento", back_populates="idoso")
    historico = relationship("HistoricoLigacao", back_populates="idoso")
    familiares = relationship("MembroFamilia", back_populates="idoso")
    legado_digital = relationship("LegadoDigital", back_populates="idoso")
    sinais_vitais = relationship("SinaisVitais", back_populates="idoso")
    insights_psicologia = relationship("PsicologiaInsight", back_populates="idoso")
    topicos_afetivos = relationship("TopicoAfetivo", back_populates="idoso")
    memoria = relationship("IdosoMemoria", back_populates="idoso")
    perfil_clinico = relationship("IdosoPerfilClinico", back_populates="idoso", uselist=False)
    protocolos = relationship("ProtocoloAlerta", back_populates="idoso")
    consumos = relationship("FaturamentoConsumo", back_populates="idoso")
    timeline = relationship("Timeline", back_populates="idoso")


class MembroFamilia(Base):
    __tablename__ = "membros_familia"
    id = Column(Integer, primary_key=True)
    idoso_id = Column(Integer, ForeignKey('idosos.id'))
    parent_id = Column(Integer, ForeignKey('membros_familia.id'), nullable=True)
    nome = Column(String, nullable=False)
    parentesco = Column(String, nullable=False)
    foto_url = Column(Text)
    is_responsavel = Column(Boolean, default=False)
    telefone = Column(String)
    criado_em = Column(DateTime, default=datetime.datetime.now)
    atualizado_em = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    idoso = relationship("Idoso", back_populates="familiares")


class IdosoMemoria(Base):
    __tablename__ = "idosos_memoria"
    id = Column(Integer, primary_key=True)
    idoso_id = Column(Integer, ForeignKey('idosos.id'))
    categoria = Column(String, nullable=False)
    chave = Column(String, nullable=False)
    valor = Column(Text, nullable=False)
    relevancia = Column(String, default='media')
    criado_em = Column(DateTime, default=datetime.datetime.now)
    atualizado_em = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    idoso = relationship("Idoso", back_populates="memoria")


class IdosoPerfilClinico(Base):
    __tablename__ = "idosos_perfil_clinico"
    idoso_id = Column(Integer, ForeignKey('idosos.id'), primary_key=True)
    tipo_sanguineo = Column(String)
    alergias = Column(Text)
    restricoes_locomocao = Column(Text)
    doencas_cronicas = Column(Text)
    atualizado_em = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    idoso = relationship("Idoso", back_populates="perfil_clinico")


class Medicamento(Base):
    __tablename__ = "medicamentos"
    id = Column(Integer, primary_key=True)
    idoso_id = Column(Integer, ForeignKey('idosos.id'))
    nome = Column(String, nullable=False)
    principio_ativo = Column(String)
    dosagem = Column(String)
    forma = Column(String)
    horarios = Column(JSON, default=[])
    observacoes = Column(Text)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.datetime.now)
    atualizado_em = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    idoso = relationship("Idoso", back_populates="medicamentos")


class SinaisVitais(Base):
    __tablename__ = "sinais_vitais"
    id = Column(Integer, primary_key=True)
    idoso_id = Column(Integer, ForeignKey('idosos.id'))
    tipo = Column(String, nullable=False)
    valor = Column(String, nullable=False)
    unidade = Column(String)
    metodo = Column(String, default='voz_ia')
    data_medicao = Column(DateTime, default=datetime.datetime.now)
    observacao = Column(Text)

    idoso = relationship("Idoso", back_populates="sinais_vitais")


class Agendamento(Base):
    __tablename__ = "agendamentos"
    id = Column(Integer, primary_key=True)
    idoso_id = Column(Integer, ForeignKey('idosos.id'))
    tipo = Column(String, nullable=False)
    data_hora_agendada = Column(DateTime, nullable=False)
    data_hora_realizada = Column(DateTime)
    max_retries = Column(Integer, default=3)
    retry_interval_minutes = Column(Integer, default=15)
    tentativas_realizadas = Column(Integer, default=0)
    proxima_tentativa = Column(DateTime)
    escalation_policy = Column(String, default='alert_family')
    status = Column(String, default='agendado')
    gemini_session_handle = Column(String)
    ultima_interacao_estado = Column(JSON)
    session_expires_at = Column(DateTime)
    dados_tarefa = Column(JSON, default={})
    prioridade = Column(String, default='normal')
    criado_por = Column(String, default='sistema')
    criado_em = Column(DateTime, default=datetime.datetime.now)
    atualizado_em = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    idoso = relationship("Idoso", back_populates="agendamentos")


class HistoricoLigacao(Base):
    __tablename__ = "historico_ligacoes"
    id = Column(Integer, primary_key=True)
    agendamento_id = Column(Integer, ForeignKey('agendamentos.id'))
    idoso_id = Column(Integer, ForeignKey('idosos.id'))
    twilio_call_sid = Column(String)
    stream_sid = Column(String)
    inicio_chamada = Column(DateTime, default=datetime.datetime.now)
    fim_chamada = Column(DateTime)
    duracao_segundos = Column(Integer)
    modelo_utilizado = Column(String)
    voice_name = Column(String)
    config_snapshot = Column(JSON)
    qualidade_audio = Column(String)
    interrupcoes_detectadas = Column(Integer, default=0)
    latencia_media_ms = Column(Integer)
    packets_perdidos = Column(Integer, default=0)
    vad_false_positives = Column(Integer, default=0)
    tarefa_concluida = Column(Boolean, default=False)
    objetivo_alcancado = Column(Boolean)
    motivo_falha = Column(Text)
    transcricao_completa = Column(Text)
    transcricao_resumo = Column(Text)
    sentimento_geral = Column(String)
    sentimento_intensidade = Column(Integer)
    acoes_registradas = Column(JSON, default=[])
    tokens_gemini = Column(Integer, default=0)
    minutos_twilio = Column(Integer, default=0)
    criado_em = Column(DateTime, default=datetime.datetime.now)

    idoso = relationship("Idoso", back_populates="historico")


class Alerta(Base):
    __tablename__ = "alertas"
    id = Column(Integer, primary_key=True)
    idoso_id = Column(Integer, ForeignKey('idosos.id'))
    ligacao_id = Column(Integer, ForeignKey('historico_ligacoes.id'), nullable=True)
    tipo = Column(String, nullable=False)
    severidade = Column(String, nullable=False)
    mensagem = Column(Text, nullable=False)
    contexto_adicional = Column(JSON, default={})
    destinatarios = Column(JSON, nullable=False)
    enviado = Column(Boolean, default=False)
    data_envio = Column(DateTime)
    visualizado = Column(Boolean, default=False)
    data_visualizacao = Column(DateTime)
    resolvido = Column(Boolean, default=False)
    data_resolucao = Column(DateTime)
    resolucao_nota = Column(Text)
    criado_em = Column(DateTime, default=datetime.datetime.now)


class ProtocoloAlerta(Base):
    __tablename__ = "protocolos_alerta"
    id = Column(Integer, primary_key=True)
    idoso_id = Column(Integer, ForeignKey('idosos.id'))
    nome = Column(String, default='Protocolo Padrão')
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.datetime.now)
    atualizado_em = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    idoso = relationship("Idoso", back_populates="protocolos")
    etapas = relationship("ProtocoloEtapa", back_populates="protocolo")


class ProtocoloEtapa(Base):
    __tablename__ = "protocolo_etapas"
    id = Column(Integer, primary_key=True)
    protocolo_id = Column(Integer, ForeignKey('protocolos_alerta.id'))
    ordem = Column(Integer, nullable=False)
    acao = Column(String, nullable=False)
    delay_minutos = Column(Integer, default=5)
    tentativas = Column(Integer, default=1)
    contato_alvo = Column(String)
    criado_em = Column(DateTime, default=datetime.datetime.now)
    atualizado_em = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    protocolo = relationship("ProtocoloAlerta", back_populates="etapas")


class PsicologiaInsight(Base):
    __tablename__ = "psicologia_insights"
    id = Column(Integer, primary_key=True)
    idoso_id = Column(Integer, ForeignKey('idosos.id'))
    tipo = Column(String, nullable=False)
    mensagem = Column(Text, nullable=False)
    data_insight = Column(DateTime, default=datetime.datetime.now)
    relevancia = Column(String, default='media')

    idoso = relationship("Idoso", back_populates="insights_psicologia")


class TopicoAfetivo(Base):
    __tablename__ = "topicos_afetivos"
    id = Column(Integer, primary_key=True)
    idoso_id = Column(Integer, ForeignKey('idosos.id'))
    topico = Column(String, nullable=False)
    frequencia = Column(Integer, default=1)
    sentimento_associado = Column(String)
    ultima_mencao = Column(DateTime, default=datetime.datetime.now)

    idoso = relationship("Idoso", back_populates="topicos_afetivos")


class AssinaturaEntidade(Base):
    __tablename__ = "assinaturas_entidade"
    id = Column(Integer, primary_key=True)
    entidade_nome = Column(String, nullable=False)
    status = Column(String, default='ativo')
    plano_id = Column(String, nullable=False)
    data_proxima_cobranca = Column(Date)
    limite_minutos = Column(Integer, default=1000)
    minutos_consumidos = Column(Integer, default=0)
    criado_em = Column(DateTime, default=datetime.datetime.now)
    atualizado_em = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class FaturamentoConsumo(Base):
    __tablename__ = "faturamento_consumo"
    id = Column(Integer, primary_key=True)
    idoso_id = Column(Integer, ForeignKey('idosos.id'))
    mes_referencia = Column(Integer, nullable=False)
    ano_referencia = Column(Integer, nullable=False)
    total_tokens = Column(Integer, default=0)
    total_minutos = Column(Integer, default=0)
    custo_total_estimado = Column(Numeric(10, 2), default=0.00)
    criado_em = Column(DateTime, default=datetime.datetime.now)

    idoso = relationship("Idoso", back_populates="consumos")


class Configuracao(Base):
    __tablename__ = "configuracoes_sistema"
    id = Column(Integer, primary_key=True)
    chave = Column(String, unique=True, nullable=False)
    valor = Column(Text)
    tipo = Column(String, nullable=False)
    categoria = Column(String, nullable=False)
    descricao = Column(Text)
    ativa = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.datetime.now)
    atualizado_em = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class PromptTemplate(Base):
    __tablename__ = "prompt_templates"
    id = Column(Integer, primary_key=True)
    nome = Column(String, unique=True, nullable=False)
    versao = Column(String, default='v1')
    template = Column(Text, nullable=False)
    variaveis_esperadas = Column(JSON, default=[])
    tipo = Column(String, nullable=False)
    ativo = Column(Boolean, default=True)
    descricao = Column(Text)
    criado_em = Column(DateTime, default=datetime.datetime.now)
    atualizado_em = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class FunctionDefinition(Base):
    __tablename__ = "function_definitions"
    id = Column(Integer, primary_key=True)
    nome = Column(String, unique=True, nullable=False)
    descricao = Column(Text, nullable=False)
    parametros = Column(JSON, nullable=False)
    tipo_tarefa = Column(String, nullable=False)
    handler_path = Column(String, nullable=False)
    validations = Column(JSON, default={})
    requires_confirmation = Column(Boolean, default=False)
    max_executions_per_call = Column(Integer, default=1)
    ativa = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.datetime.now)
    atualizado_em = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class LegadoDigital(Base):
    __tablename__ = "idosos_legado_digital"
    id = Column(Integer, primary_key=True)
    idoso_id = Column(Integer, ForeignKey('idosos.id'))
    tipo = Column(String, nullable=False)
    titulo = Column(String, nullable=False)
    url_midia = Column(Text, nullable=False) 
    destinatario = Column(String)
    protegido = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.datetime.now)

    idoso = relationship("Idoso", back_populates="legado_digital")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    usuario_email = Column(String)
    acao = Column(String, nullable=False)
    recurso = Column(String)
    detalhes = Column(Text)
    ip_address = Column(String)
    criado_em = Column(DateTime, default=datetime.datetime.now)


# Circuit Breaker States (Extra functionality used in some handlers)
class CircuitBreakerState(Base):
    __tablename__ = "circuit_breaker_states"
    id = Column(Integer, primary_key=True)
    service_name = Column(String, unique=True)
    state = Column(String, default="closed")
    failure_count = Column(Integer, default=0)
    last_failure_time = Column(DateTime, nullable=True)


class RateLimit(Base):
    __tablename__ = "rate_limits"
    id = Column(Integer, primary_key=True)
    endpoint = Column(String, unique=True)
    limit_count = Column(Integer, default=100)
    interval_seconds = Column(Integer, default=60)


class Timeline(Base):
    __tablename__ = "timeline"
    id = Column(Integer, primary_key=True)
    idoso_id = Column(Integer, ForeignKey('idosos.id'))
    tipo = Column(String, nullable=False)
    subtipo = Column(String)
    titulo = Column(String, nullable=False)
    descricao = Column(Text)
    data = Column(DateTime, default=datetime.datetime.now)
    criado_em = Column(DateTime, default=datetime.datetime.now)

    idoso = relationship("Idoso", back_populates="timeline")


# --- IA Avançada ---

class PadraoComportamento(Base):
    __tablename__ = "padroes_comportamento"
    
    id = Column(Integer, primary_key=True)
    idoso_id = Column(Integer, nullable=False)
    tipo_padrao = Column(String(50), nullable=False)
    descricao = Column(Text, nullable=False)
    frequencia = Column(String(20))
    confianca = Column(Numeric(3, 2))
    primeira_deteccao = Column(DateTime, default=datetime.datetime.utcnow)
    ultima_confirmacao = Column(DateTime, default=datetime.datetime.utcnow)
    ocorrencias = Column(Integer, default=1)
    dados_estatisticos = Column(JSONB)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class PredicaoEmergencia(Base):
    __tablename__ = "predicoes_emergencia"
    
    id = Column(Integer, primary_key=True)
    idoso_id = Column(Integer, nullable=False)
    tipo_emergencia = Column(String(50), nullable=False)
    probabilidade = Column(Numeric(3, 2), nullable=False)
    nivel_risco = Column(String(20), nullable=False)
    fatores_contribuintes = Column(JSONB, nullable=False)
    sinais_detectados = Column(JSONB)
    recomendacoes = Column(JSONB)
    data_predicao = Column(DateTime, default=datetime.datetime.utcnow)
    validade_ate = Column(DateTime)
    confirmada = Column(Boolean, default=False)
    data_confirmacao = Column(DateTime)
    falso_positivo = Column(Boolean, default=False)
    criado_em = Column(DateTime, default=datetime.datetime.utcnow)


# =====================================================
# HEALTH DATA MODELS (Sistema de Monitoramento de Saúde)
# =====================================================

class Usuario(Base):
    """Usuários do sistema de monitoramento de saúde"""
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True)
    matricula = Column(String(50))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relacionamentos
    atividades = relationship("Atividade", back_populates="usuario", cascade="all, delete-orphan")
    sinais_vitais = relationship("SinaisVitaisHealth", back_populates="usuario", cascade="all, delete-orphan")
    sono = relationship("Sono", back_populates="usuario", cascade="all, delete-orphan")
    medicoes_corporais = relationship("MedicaoCorporal", back_populates="usuario", cascade="all, delete-orphan")
    nutricao = relationship("Nutricao", back_populates="usuario", cascade="all, delete-orphan")
    ciclo_menstrual = relationship("CicloMenstrual", back_populates="usuario", cascade="all, delete-orphan")


class Atividade(Base):
    """Registros de atividade física e exercícios"""
    __tablename__ = "atividade"
    
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    passos = Column(Integer, default=0)
    calorias_queimadas = Column(Numeric(10, 2))
    distancia_km = Column(Numeric(10, 2))
    andares_subidos = Column(Integer)
    velocidade_media = Column(Numeric(5, 2))
    cadencia_pedalada = Column(Integer)
    potencia_watts = Column(Integer)
    tipo_exercicio = Column(String(100))  # corrida, natação, ciclismo, etc
    timestamp_coleta = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relacionamento
    usuario = relationship("Usuario", back_populates="atividades")


class SinaisVitaisHealth(Base):
    """Sinais vitais coletados de dispositivos de saúde"""
    __tablename__ = "sinais_vitais_health"
    
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    bpm = Column(Integer)  # Batimentos por minuto
    bpm_repouso = Column(Integer)  # BPM em repouso
    pressao_sistolica = Column(Integer)  # Ex: 120
    pressao_diastolica = Column(Integer)  # Ex: 80
    spo2 = Column(Numeric(5, 2))  # Saturação de Oxigênio (0-100)
    glicose_sangue = Column(Numeric(10, 2))  # mg/dL
    frequencia_respiratoria = Column(Integer)  # Respirações por minuto
    timestamp_coleta = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relacionamento
    usuario = relationship("Usuario", back_populates="sinais_vitais")


class Sono(Base):
    """Registros de sessões de sono e qualidade"""
    __tablename__ = "sono"
    
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    duracao_total_minutos = Column(Integer)
    estagio_leve_minutos = Column(Integer)
    estagio_profundo_minutos = Column(Integer)
    estagio_rem_minutos = Column(Integer)
    tempo_acordado_minutos = Column(Integer)
    timestamp_inicio = Column(DateTime)
    timestamp_fim = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relacionamento
    usuario = relationship("Usuario", back_populates="sono")


class MedicaoCorporal(Base):
    """Medições corporais e composição"""
    __tablename__ = "medicao_corporal"
    
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    peso_kg = Column(Numeric(5, 2))
    altura_cm = Column(Numeric(5, 2))
    perc_gordura_corporal = Column(Numeric(5, 2))
    massa_ossea_kg = Column(Numeric(5, 2))
    massa_magra_kg = Column(Numeric(5, 2))
    circunferencia_cintura_cm = Column(Numeric(5, 2))
    circunferencia_quadril_cm = Column(Numeric(5, 2))
    timestamp_coleta = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relacionamento
    usuario = relationship("Usuario", back_populates="medicoes_corporais")


class Nutricao(Base):
    """Registros de nutrição e hidratação"""
    __tablename__ = "nutricao"
    
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    ingestao_agua_ml = Column(Integer)
    calorias_consumidas = Column(Integer)
    proteinas_g = Column(Numeric(10, 2))
    carboidratos_g = Column(Numeric(10, 2))
    gorduras_g = Column(Numeric(10, 2))
    vitaminas_json = Column(JSONB)  # Formato flexível para vitaminas
    timestamp_coleta = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relacionamento
    usuario = relationship("Usuario", back_populates="nutricao")


class CicloMenstrual(Base):
    """Registros do ciclo menstrual"""
    __tablename__ = "ciclo_menstrual"
    
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    data_menstruacao = Column(Date)
    teste_ovulacao = Column(String(50))  # Positivo/Negativo
    muco_cervical = Column(String(100))
    atividade_sexual = Column(Boolean)
    sintomas_json = Column(JSONB)  # Sintomas adicionais
    timestamp_coleta = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relacionamento
    usuario = relationship("Usuario", back_populates="ciclo_menstrual")
