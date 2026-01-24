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
    cuidadores = relationship("Cuidador", back_populates="idoso")


class Cuidador(Base):
    __tablename__ = "cuidadores"
    
    id = Column(Integer, primary_key=True)
    idoso_id = Column(Integer, ForeignKey('idosos.id', ondelete='CASCADE'), nullable=False)
    nome = Column(String(255), nullable=False)
    cpf = Column(String(14))
    telefone = Column(String(20), nullable=False)
    email = Column(String(255))
    parentesco = Column(String(100))
    tipo_cuidador = Column(String(50), default='familiar')
    eh_responsavel = Column(Boolean, default=False)
    eh_contato_emergencia = Column(Boolean, default=False)
    device_token = Column(Text)
    ativo = Column(Boolean, default=True)
    observacoes = Column(Text)
    criado_em = Column(DateTime, default=datetime.datetime.now)
    atualizado_em = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    prioridade = Column(Integer, default=1)
    metodo_preferido = Column(String(20), default='push')
    
    # Relacionamento
    idoso = relationship("Idoso", back_populates="cuidadores")


class MembroFamilia(Base):
    __tablename__ = "membros_familia"
    id = Column(Integer, primary_key=True)
    idoso_id = Column(Integer, ForeignKey('idosos.id'))
    parent_id = Column(Integer, ForeignKey('membros_familia.id'), nullable=True)
    nome = Column(String, nullable=False)
    parentesco = Column(String, nullable=False)
    telefone = Column(String)
    email = Column(String)  # ✅ Added email field
    foto_url = Column(Text)
    is_responsavel = Column(Boolean, default=False)
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
    catalogo_ref_id = Column(Integer, ForeignKey('catalogo_farmaceutico.id'), nullable=True) # O VITAL LINK
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
    catalogo = relationship("CatalogoFarmaceutico")


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
    # Link Vital conforme diagrama de arquitetura (Operational Module)
    medicamento_id = Column(Integer, ForeignKey('medicamentos.id'), nullable=True)
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


class BehavioralNote(Base):
    __tablename__ = "behavioral_notes"
    
    id = Column(Integer, primary_key=True)
    idoso_id = Column(Integer, ForeignKey('idosos.id', ondelete='CASCADE'), nullable=False)
    category = Column(String(50), nullable=False)
    observation = Column(Text, nullable=False)
    confidence = Column(Numeric(3, 2))
    evidence = Column(JSONB, default=[])
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    active = Column(Boolean, default=True)


class AutomationTask(Base):
    __tablename__ = "automation_tasks"
    
    id = Column(Integer, primary_key=True)
    idoso_id = Column(Integer, ForeignKey('idosos.id', ondelete='CASCADE'), nullable=False)
    task_type = Column(String(50), nullable=False)
    service_name = Column(String(100), nullable=False)
    task_params = Column(JSONB, nullable=False)
    status = Column(String(50), default='pending')
    approval_required = Column(Boolean, default=True)
    approved_by = Column(Integer)
    approved_at = Column(DateTime)
    execution_log = Column(JSONB)
    screenshots = Column(JSONB)
    result = Column(JSONB)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    executed_at = Column(DateTime)
    completed_at = Column(DateTime)


class AutomationApproval(Base):
    __tablename__ = "automation_approvals"
    
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('automation_tasks.id', ondelete='CASCADE'), nullable=False)
    approver_id = Column(Integer, nullable=False)
    approval_status = Column(String(20))
    approval_reason = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    responded_at = Column(DateTime)


class AutomationExecutionLog(Base):
    __tablename__ = "automation_execution_log"
    
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('automation_tasks.id', ondelete='CASCADE'), nullable=False)
    step_number = Column(Integer, nullable=False)
    step_name = Column(String(200), nullable=False)
    step_status = Column(String(50))
    screenshot_url = Column(Text)
    step_data = Column(JSONB)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class EpisodicMemory(Base):
    __tablename__ = "episodic_memories"
    
    id = Column(Integer, primary_key=True)
    idoso_id = Column(Integer, ForeignKey('idosos.id', ondelete='CASCADE'), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    speaker = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    emotion = Column(String(50))
    importance = Column(Numeric(3, 2), default=0.5)
    topics = Column(JSONB)
    session_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class ABTestConfig(Base):
    __tablename__ = "ab_test_config"
    
    id = Column(Integer, primary_key=True)
    test_name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    enabled = Column(Boolean, default=True)
    percentage_group_a = Column(Integer, default=50)
    group_a_name = Column(String(50), default='thinking_mode')
    group_b_name = Column(String(50), default='normal_mode')
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    ended_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class ABTestAssignment(Base):
    __tablename__ = "ab_test_assignments"
    
    id = Column(Integer, primary_key=True)
    test_name = Column(String(100), nullable=False)
    idoso_id = Column(Integer, ForeignKey('idosos.id', ondelete='CASCADE'), nullable=False)
    assigned_group = Column(String(50), nullable=False)
    assigned_at = Column(DateTime, default=datetime.datetime.utcnow)


class ABTestMetric(Base):
    __tablename__ = "ab_test_metrics"
    
    id = Column(Integer, primary_key=True)
    test_name = Column(String(100), nullable=False)
    idoso_id = Column(Integer, ForeignKey('idosos.id', ondelete='CASCADE'), nullable=False)
    assigned_group = Column(String(50), nullable=False)
    metric_type = Column(String(100), nullable=False)
    metric_value = Column(Numeric(10, 4))
    metadata = Column(JSONB)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class HealthThinkingAudit(Base):
    __tablename__ = "health_thinking_audit"
    
    id = Column(Integer, primary_key=True)
    idoso_id = Column(Integer, ForeignKey('idosos.id', ondelete='CASCADE'), nullable=False)
    thought_process = Column(Text, nullable=False)
    risk_level = Column(String(20))
    caregiver_notified = Column(Boolean, default=False)
    notified_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Biografia(Base):
    __tablename__ = "biografias"
    
    id = Column(Integer, primary_key=True)
    idoso_id = Column(Integer, ForeignKey('idosos.id', ondelete='CASCADE'), nullable=False)
    titulo = Column(String(200), nullable=False)
    conteudo = Column(Text, nullable=False)
    data_acontecimento = Column(Date)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


# =====================================================
# INTELLIGENCE MODULE (O Cérebro Farmacêutico)
# =====================================================

class CatalogoFarmaceutico(Base):
    __tablename__ = "catalogo_farmaceutico"
    
    id = Column(Integer, primary_key=True)
    nome_oficial = Column(String(500), nullable=False) # Princípio Ativo
    nomes_comerciais = Column(Text)
    classe_terapeutica = Column(String(300))
    apresentacao_padrao = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.now)

    # Relacionamentos de Inteligência
    dosagem_ref = relationship("ReferenciaDosagem", back_populates="catalogo", uselist=False)
    riscos_geriatricos = relationship("RiscosGeriatricos", back_populates="catalogo", uselist=False)
    
    # Interações (Complexo N:N self-referential via tabela associativa)
    # Por simplificação, acessaremos via queries diretas no repo

class ReferenciaDosagem(Base):
    __tablename__ = "referencia_dosagem"
    
    id = Column(Integer, primary_key=True)
    catalogo_id = Column(Integer, ForeignKey('catalogo_farmaceutico.id', ondelete='CASCADE'))
    dose_maxima_mg = Column(Numeric(10, 2))
    alerta_renal = Column(Text)
    faixa_etaria_alvo = Column(String(50))
    
    catalogo = relationship("CatalogoFarmaceutico", back_populates="dosagem_ref")

class RiscosGeriatricos(Base):
    __tablename__ = "riscos_geriatricos"
    
    id = Column(Integer, primary_key=True)
    catalogo_id = Column(Integer, ForeignKey('catalogo_farmaceutico.id', ondelete='CASCADE'))
    risco_queda = Column(Boolean, default=False)
    confusao_mental = Column(Boolean, default=False)
    agravamento_demencia = Column(Boolean, default=False)
    risco_cardiaco = Column(Boolean, default=False)
    observacoes = Column(Text)
    fonte_referencia = Column(String(100))
    
    catalogo = relationship("CatalogoFarmaceutico", back_populates="riscos_geriatricos")

class InteracoesRisco(Base):
    __tablename__ = "interacoes_risco"
    
    id = Column(Integer, primary_key=True)
    catalogo_id_a = Column(Integer, ForeignKey('catalogo_farmaceutico.id'))
    catalogo_id_b = Column(Integer, ForeignKey('catalogo_farmaceutico.id'))
    nivel_perigo = Column(String(20), nullable=False) # FATAL, ALTO, MEDIO
    descricao = Column(Text, nullable=False)
    mecanismo = Column(String(200))
    manejo_clinico = Column(Text)

# =====================================================
# HEALTH DATA MODELS (Sistema de Monitoramento de Saúde)
# =====================================================


class Usuario(Base):
    """Usuários do sistema de monitoramento de saúde"""
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True)
    senha_hash = Column(String(255))
    telefone = Column(String(50))
    tipo = Column(String(50), default='viewer')
    ativo = Column(Boolean, default=True)
    email_verificado = Column(Boolean, default=False)
    cpf = Column(String(20))
    data_nascimento = Column(Date)
    
    matricula = Column(String(50)) # Keeping this if needed for legacy or specific business logic
    
    criado_em = Column(DateTime, default=datetime.datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Aliases for compatibility with old code if strictly necessary, but better to migrate usage
    # created_at = criado_em 
    # updated_at = atualizado_em
    
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


# =====================================================================
# MODELOS DE SAÚDE MENTAL
# =====================================================================

class MentalHealthAssessment(Base):
    """Avaliações clínicas de saúde mental (PHQ-9, GAD-7, C-SSRS, etc)"""
    __tablename__ = "mental_health_assessments"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('idosos.id', ondelete='CASCADE'), nullable=False)
    scale_type = Column(String(50), nullable=False)  # PHQ9, GAD7, C-SSRS, PSS10, Y-BOCS, PCL5
    score = Column(Integer, nullable=False)
    severity_level = Column(String(50))  # minimal, mild, moderate, moderately_severe, severe
    assessed_at = Column(DateTime, default=datetime.datetime.now)
    questions_answers = Column(JSONB, default=[])
    professional_id = Column(Integer, ForeignKey('cuidadores.id', ondelete='SET NULL'))
    notes = Column(Text)
    interpretation = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    # Relacionamentos
    patient = relationship("Idoso", backref="mental_health_assessments")
    professional = relationship("Cuidador", backref="mental_health_assessments")


class MoodDiary(Base):
    """Diário de humor (manhã, tarde, noite)"""
    __tablename__ = "mood_diary"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('idosos.id', ondelete='CASCADE'), nullable=False)
    date = Column(Date, nullable=False, default=datetime.date.today)
    time_of_day = Column(String(20), nullable=False)  # morning, afternoon, evening
    mood_score = Column(Integer)  # 1-10
    anxiety_level = Column(Integer)  # 1-10
    energy_level = Column(Integer)  # 1-10
    sleep_quality = Column(Integer)  # 1-10
    sleep_hours = Column(Numeric(4, 2))
    awakenings = Column(Integer)
    notes = Column(Text)
    symptoms = Column(JSONB, default=[])
    triggers = Column(JSONB, default=[])
    helpful_activities = Column(JSONB, default=[])
    physical_symptoms = Column(JSONB, default=[])
    intrusive_thoughts = Column(Boolean, default=False)
    intrusive_thoughts_description = Column(Text)
    accomplished_planned_activities = Column(Boolean)
    created_at = Column(DateTime, default=datetime.datetime.now)

    # Relacionamento
    patient = relationship("Idoso", backref="mood_diary_entries")


class MentalHealthCondition(Base):
    """Diagnósticos formais de condições de saúde mental"""
    __tablename__ = "mental_health_conditions"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('idosos.id', ondelete='CASCADE'), nullable=False)
    condition_name = Column(String(100), nullable=False)
    condition_category = Column(String(50))  # mood_disorder, anxiety_disorder, etc
    severity = Column(String(50))  # mild, moderate, severe
    diagnosed_by = Column(Integer, ForeignKey('cuidadores.id', ondelete='SET NULL'))
    diagnosis_date = Column(Date)
    icd_10_code = Column(String(10))
    current_status = Column(String(50), default='active')  # active, in_remission, resolved
    notes = Column(Text)
    comorbidities = Column(JSONB, default=[])
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    # Relacionamentos
    patient = relationship("Idoso", backref="mental_health_conditions")
    diagnosing_professional = relationship("Cuidador", backref="diagnosed_conditions")


class Symptom(Base):
    """Rastreamento granular de sintomas"""
    __tablename__ = "symptoms"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('idosos.id', ondelete='CASCADE'), nullable=False)
    symptom_name = Column(String(100), nullable=False)
    symptom_category = Column(String(50))  # cognitive, emotional, behavioral, physical, social
    severity = Column(String(50))  # mild, moderate, severe
    frequency = Column(String(50))  # rare, occasional, frequent, daily, constant
    first_occurrence = Column(Date)
    last_occurrence = Column(Date)
    related_condition_id = Column(Integer, ForeignKey('mental_health_conditions.id', ondelete='SET NULL'))
    notes = Column(Text)
    impact_on_daily_life = Column(Integer)  # 1-10
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    # Relacionamentos
    patient = relationship("Idoso", backref="symptoms")
    related_condition = relationship("MentalHealthCondition", backref="symptoms")


class Trigger(Base):
    """Gatilhos que desencadeiam sintomas/crises"""
    __tablename__ = "triggers"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('idosos.id', ondelete='CASCADE'), nullable=False)
    trigger_description = Column(String(255), nullable=False)
    trigger_category = Column(String(50))  # interpersonal, environmental, physiological, cognitive
    severity = Column(String(50))  # mild, moderate, severe
    related_symptom_id = Column(Integer, ForeignKey('symptoms.id', ondelete='SET NULL'))
    identified_at = Column(DateTime, default=datetime.datetime.now)
    last_triggered = Column(DateTime)
    frequency_count = Column(Integer, default=1)
    notes = Column(Text)
    coping_strategies = Column(JSONB, default=[])
    created_at = Column(DateTime, default=datetime.datetime.now)

    # Relacionamentos
    patient = relationship("Idoso", backref="triggers")
    related_symptom = relationship("Symptom", backref="triggers")


class TherapySession(Base):
    """Sessões de terapia/consultas psicológicas"""
    __tablename__ = "therapy_sessions"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('idosos.id', ondelete='CASCADE'), nullable=False)
    therapist_id = Column(Integer, ForeignKey('cuidadores.id', ondelete='SET NULL'))
    session_date = Column(DateTime, nullable=False)
    session_type = Column(String(50))  # individual, group, family, online, emergency
    duration_minutes = Column(Integer)
    main_topics = Column(JSONB, default=[])
    interventions_used = Column(JSONB, default=[])
    patient_mood_before = Column(Integer)  # 1-10
    patient_mood_after = Column(Integer)  # 1-10
    homework_assigned = Column(Text)
    next_session_date = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.now)

    # Relacionamentos
    patient = relationship("Idoso", backref="therapy_sessions")
    therapist = relationship("Cuidador", backref="therapy_sessions")


class CrisisEvent(Base):
    """Registro de crises/eventos críticos"""
    __tablename__ = "crisis_events"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('idosos.id', ondelete='CASCADE'), nullable=False)
    crisis_type = Column(String(50), nullable=False)  # suicidal_ideation, panic_attack, etc
    severity = Column(String(50))  # mild, moderate, severe, life_threatening
    occurred_at = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer)
    location = Column(String(100))
    precipitating_factors = Column(JSONB, default=[])
    warning_signs = Column(JSONB, default=[])
    intervention_taken = Column(JSONB, default=[])
    emergency_contacts_notified = Column(JSONB, default=[])
    hospitalization_required = Column(Boolean, default=False)
    hospital_name = Column(String(200))
    hospital_admission_date = Column(DateTime)
    hospital_discharge_date = Column(DateTime)
    follow_up_scheduled = Column(Boolean, default=False)
    follow_up_date = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.now)

    # Relacionamento
    patient = relationship("Idoso", backref="crisis_events")


class SafetyPlan(Base):
    """Planos de segurança para prevenção de crises"""
    __tablename__ = "safety_plans"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('idosos.id', ondelete='CASCADE'), nullable=False)
    created_by = Column(Integer, ForeignKey('cuidadores.id', ondelete='SET NULL'))
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    warning_signs = Column(JSONB, default=[])
    internal_coping_strategies = Column(JSONB, default=[])
    social_distractions = Column(JSONB, default=[])
    people_to_contact = Column(JSONB, default=[])
    professionals_to_contact = Column(JSONB, default=[])
    crisis_hotlines = Column(JSONB, default=[])
    environment_safety = Column(JSONB, default=[])
    reasons_for_living = Column(JSONB, default=[])
    active = Column(Boolean, default=True)

    # Relacionamentos
    patient = relationship("Idoso", backref="safety_plans")
    creator = relationship("Cuidador", backref="created_safety_plans")


class MedicationSideEffect(Base):
    """Efeitos colaterais de medicamentos"""
    __tablename__ = "medication_side_effects"

    id = Column(Integer, primary_key=True)
    medication_log_id = Column(Integer, ForeignKey('agendamentos.id', ondelete='CASCADE'))
    patient_id = Column(Integer, ForeignKey('idosos.id', ondelete='CASCADE'), nullable=False)
    medication_id = Column(Integer, ForeignKey('medicamentos.id', ondelete='CASCADE'), nullable=False)
    side_effect_name = Column(String(100), nullable=False)
    severity = Column(String(50))  # mild, moderate, severe
    reported_at = Column(DateTime, default=datetime.datetime.now)
    duration_hours = Column(Integer)
    required_medical_attention = Column(Boolean, default=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.now)

    # Relacionamentos
    patient = relationship("Idoso", backref="medication_side_effects")
    medication = relationship("Medicamento", backref="side_effects")


class NLPConversationAnalysis(Base):
    """Análise NLP de conversas com IA"""
    __tablename__ = "nlp_conversation_analysis"

    id = Column(Integer, primary_key=True)
    conversation_session_id = Column(Integer, ForeignKey('conversation_sessions.id', ondelete='CASCADE'))
    message_id = Column(Integer, ForeignKey('conversation_messages.id', ondelete='CASCADE'))
    patient_id = Column(Integer, ForeignKey('idosos.id', ondelete='CASCADE'), nullable=False)
    sentiment_score = Column(Numeric(5, 4))  # -1 to 1
    sentiment_label = Column(String(20))  # very_negative, negative, neutral, positive, very_positive
    detected_keywords = Column(JSONB, default=[])
    danger_flags = Column(JSONB, default=[])  # suicidal_ideation, self_harm, etc
    extracted_entities = Column(JSONB, default={})
    topic_classification = Column(JSONB, default=[])
    analyzed_at = Column(DateTime, default=datetime.datetime.now)

    # Relacionamentos
    patient = relationship("Idoso", backref="nlp_analyses")


class MLPrediction(Base):
    """Predições de modelos de Machine Learning"""
    __tablename__ = "ml_predictions"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('idosos.id', ondelete='CASCADE'), nullable=False)
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50))
    prediction_type = Column(String(50))  # crisis_24h, suicide_risk, etc
    prediction_value = Column(Numeric(5, 4))
    prediction_label = Column(String(50))
    confidence_score = Column(Numeric(5, 4))
    features_used = Column(JSONB)
    predicted_at = Column(DateTime, default=datetime.datetime.now)
    valid_until = Column(DateTime)
    actual_outcome = Column(String(50))
    outcome_recorded_at = Column(DateTime)

    # Relacionamento
    patient = relationship("Idoso", backref="ml_predictions")


class TreatmentGoal(Base):
    """Objetivos terapêuticos"""
    __tablename__ = "treatment_goals"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('idosos.id', ondelete='CASCADE'), nullable=False)
    therapist_id = Column(Integer, ForeignKey('cuidadores.id', ondelete='SET NULL'))
    goal_description = Column(Text, nullable=False)
    goal_category = Column(String(50))  # symptom_reduction, behavioral_change, etc
    target_date = Column(Date)
    status = Column(String(50), default='active')  # active, achieved, partially_achieved, not_achieved
    progress_percentage = Column(Integer, default=0)
    measurable_criteria = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    # Relacionamentos
    patient = relationship("Idoso", backref="treatment_goals")
    therapist = relationship("Cuidador", backref="assigned_treatment_goals")


class AssessmentScaleReference(Base):
    """Referência para questões das escalas de avaliação"""
    __tablename__ = "assessment_scales_reference"

    id = Column(Integer, primary_key=True)
    scale_type = Column(String(50), nullable=False)
    version = Column(String(20), default='1.0')
    language = Column(String(10), default='pt-BR')
    questions = Column(JSONB, nullable=False)
    scoring_rules = Column(JSONB, nullable=False)
    interpretation_guide = Column(JSONB, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)
