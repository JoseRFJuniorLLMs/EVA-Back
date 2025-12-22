-- ================================================================
-- EVA ENTERPRISE - SCHEMA SQL COMPLETO
-- Versão: 6.0 (Suporte a Psicologia IA, Legado e Sinais Vitais)
-- Data: 2025-12-21
-- ================================================================

-- ================================================================
-- TABELA 1: configuracoes_sistema
-- Substitui TODAS as constantes hardcoded
-- ================================================================
CREATE TABLE configuracoes_sistema (
    id SERIAL PRIMARY KEY,
    chave VARCHAR(255) UNIQUE NOT NULL,
    valor TEXT NOT NULL,
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('string', 'integer', 'float', 'boolean', 'json')),
    categoria VARCHAR(100) NOT NULL,
    descricao TEXT,
    ativa BOOLEAN DEFAULT true,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Índices para performance
    CONSTRAINT chk_chave_formato CHECK (chave ~* '^[a-z0-9_.]+$')
);

CREATE INDEX idx_config_chave ON configuracoes_sistema(chave) WHERE ativa = true;
CREATE INDEX idx_config_categoria ON configuracoes_sistema(categoria) WHERE ativa = true;

-- Trigger para atualizar timestamp
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.atualizado_em = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_config_timestamp
BEFORE UPDATE ON configuracoes_sistema
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- ================================================================
-- DADOS INICIAIS: configuracoes_sistema
-- ================================================================
INSERT INTO configuracoes_sistema (chave, valor, tipo, categoria, descricao) VALUES
-- Gemini Model
('gemini.model_id', 'gemini-2.0-flash-exp', 'string', 'gemini', 'ID do modelo Gemini Live'),
('gemini.temperature', '0.8', 'float', 'gemini', 'Temperatura do modelo (0.0-2.0)'),
('gemini.max_output_tokens', '8192', 'integer', 'gemini', 'Máximo de tokens na resposta'),
('gemini.top_p', '0.95', 'float', 'gemini', 'Top-p sampling'),
('gemini.top_k', '40', 'integer', 'gemini', 'Top-k sampling'),

-- Gemini Voice
('gemini.voice_name', 'Aoede', 'string', 'gemini', 'Nome da voz (Puck, Charon, Kore, Fenrir, Aoede)'),
('gemini.response_modalities', '["AUDIO"]', 'json', 'gemini', 'Modalidades de resposta'),

-- Gemini Session
('gemini.session_resumption_enabled', 'true', 'boolean', 'gemini', 'Habilita continuidade de sessão'),
('gemini.session_resumption_ttl_hours', '2', 'integer', 'gemini', 'Tempo de vida do session handle (horas)'),
('gemini.context_window_trigger_tokens', '100000', 'integer', 'gemini', 'Quando comprimir contexto'),
('gemini.context_window_target_tokens', '80000', 'integer', 'gemini', 'Alvo após compressão'),

-- Audio Processing
('audio.sample_rate', '16000', 'integer', 'audio', 'Taxa de amostragem (Hz)'),
('audio.channels', '1', 'integer', 'audio', 'Número de canais'),
('audio.chunk_size_bytes', '8000', 'integer', 'audio', 'Tamanho do chunk de áudio'),
('audio.buffer_size_bytes', '20000', 'integer', 'audio', 'Tamanho do buffer'),

-- Audio Detection (RMS + VAD)
('audio.speech_detection_rms', '400', 'integer', 'audio', 'Threshold RMS para detecção inicial'),
('audio.silence_threshold_seconds', '1.5', 'float', 'audio', 'Silêncio para fim de turno'),
('audio.vad_enabled', 'true', 'boolean', 'audio', 'Habilita Voice Activity Detection'),
('audio.vad_aggressiveness', '2', 'integer', 'audio', 'Agressividade VAD (0-3)'),
('audio.vad_frame_duration_ms', '30', 'integer', 'audio', 'Duração do frame VAD (10, 20 ou 30ms)'),

-- Twilio
('twilio.from_number', '+1234567890', 'string', 'twilio', 'Número Twilio para fazer chamadas'),
('twilio.timeout_seconds', '60', 'integer', 'twilio', 'Timeout para estabelecer chamada'),
('twilio.max_call_duration_seconds', '600', 'integer', 'twilio', 'Duração máxima da chamada (10min)'),

-- Features
('features.function_calling_enabled', 'true', 'boolean', 'features', 'Habilita Function Calling'),
('features.telemetry_enabled', 'true', 'boolean', 'features', 'Habilita telemetria de qualidade'),
('features.sms_alerts_enabled', 'true', 'boolean', 'features', 'Habilita alertas por SMS'),
('features.whatsapp_alerts_enabled', 'false', 'boolean', 'features', 'Habilita alertas por WhatsApp'),

-- Retry Policy (Default)
('retry.max_attempts', '3', 'integer', 'retry', 'Máximo de tentativas de ligação'),
('retry.interval_minutes', '15', 'integer', 'retry', 'Intervalo entre tentativas'),
('retry.escalation_policy', 'alert_family', 'string', 'retry', 'Política de escalonamento (alert_family, emergency_contact)'),

-- Telemetry
('telemetry.log_level', 'info', 'string', 'telemetry', 'Nível de log (debug, info, warn, error)'),
('telemetry.track_vad_false_positives', 'true', 'boolean', 'telemetry', 'Rastreia falsos positivos do VAD'),

-- Sistema
('sistema.timezone_default', 'America/Sao_Paulo', 'string', 'sistema', 'Fuso horário padrão'),
('sistema.maintenance_mode', 'false', 'boolean', 'sistema', 'Modo manutenção (bloqueia novas chamadas)');

-- ================================================================
-- TABELA 2: prompt_templates
-- Templates Mustache/Chevron personalizáveis
-- ================================================================
CREATE TABLE prompt_templates (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) UNIQUE NOT NULL,
    versao VARCHAR(20) NOT NULL DEFAULT 'v1',
    template TEXT NOT NULL,
    variaveis_esperadas JSONB NOT NULL DEFAULT '[]',
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('system_base', 'task_specific', 'recovery', 'escalation')),
    ativo BOOLEAN DEFAULT true,
    descricao TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_prompt_nome ON prompt_templates(nome) WHERE ativo = true;
CREATE INDEX idx_prompt_tipo ON prompt_templates(tipo) WHERE ativo = true;

CREATE TRIGGER trigger_prompt_timestamp
BEFORE UPDATE ON prompt_templates
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- ================================================================
-- DADOS INICIAIS: prompt_templates
-- ================================================================
INSERT INTO prompt_templates (nome, versao, template, variaveis_esperadas, tipo, descricao) VALUES
('eva_base_v2', 'v2.0', 
'Você é Eva, assistente de saúde gentil e empática especializada em cuidar de idosos.

INFORMAÇÕES DO PACIENTE:
- Nome: {{nome_idoso}}
- Idade: {{idade}} anos
- Nível Cognitivo: {{nivel_cognitivo}}
{{#limitacoes_auditivas}}
- IMPORTANTE: {{nome_idoso}} tem limitações auditivas. Fale devagar, com pausas claras e repita informações importantes.
{{/limitacoes_auditivas}}
{{#usa_aparelho_auditivo}}
- Paciente usa aparelho auditivo. Evite ruídos abruptos e mantenha tom consistente.
{{/usa_aparelho_auditivo}}

TOM DE VOZ: {{tom_voz}}

{{#primeira_interacao}}
PRIMEIRA INTERAÇÃO: Esta é a primeira vez que você fala com {{nome_idoso}}. Seja especialmente acolhedora e paciente.
{{/primeira_interacao}}

{{^primeira_interacao}}
HISTÓRICO: Você já falou com {{nome_idoso}} {{taxa_adesao}}% das vezes ele(a) seguiu as orientações.
{{/primeira_interacao}}

INSTRUÇÕES CRÍTICAS:
1. NUNCA invente informações médicas
2. SEMPRE confirme ações importantes antes de registrá-las
3. Se detectar confusão ou emergência, chame a função alert_family imediatamente
4. Fale de forma natural e conversacional, evitando jargões técnicos
5. Respeite o tempo de resposta do idoso - não apresse

PERSONALIDADE:
- Paciente e repetitiva quando necessário
- Gentil mas assertiva sobre medicamentos
- Usa exemplos do dia a dia
- Celebra pequenas conquistas',
'["nome_idoso", "idade", "nivel_cognitivo", "limitacoes_auditivas", "usa_aparelho_auditivo", "tom_voz", "primeira_interacao", "taxa_adesao"]',
'system_base',
'Template base do sistema Eva v2'),

('eva_lembrete_medicamento', 'v2.0',
'TAREFA ATUAL: Lembrete de Medicamento

MEDICAMENTO: {{medicamento}}
HORÁRIO PRESCRITO: {{horario_previsto}}
DOSAGEM: {{dosagem}}
{{#observacoes_medicas}}
OBSERVAÇÕES MÉDICAS: {{observacoes_medicas}}
{{/observacoes_medicas}}

FLUXO DA CONVERSA:
1. Cumprimente {{nome_idoso}} de forma calorosa
2. Pergunte como ele(a) está se sentindo hoje
3. Lembre sobre o medicamento {{medicamento}}
4. Confirme se já tomou ou se precisa de ajuda
5. Se NÃO tomou: pergunte gentilmente o motivo e incentive
6. Se TOMOU: parabenize e pergunte se teve algum efeito colateral
7. Registre a resposta usando a função confirm_medication

EXEMPLO DE DIÁLOGO:
Eva: "Oi {{nome_idoso}}, como está se sentindo hoje?"
Idoso: "Estou bem, obrigado."
Eva: "Que bom! Estou ligando para lembrar sobre o {{medicamento}}. Você já tomou hoje?"

ATENÇÃO:
- Se o idoso mencionar efeitos colaterais graves (tontura, dor intensa, confusão), chame alert_family IMEDIATAMENTE
- Se esqueceu mais de 2 doses consecutivas, chame alert_family com urgência "média"',
'["medicamento", "horario_previsto", "dosagem", "observacoes_medicas"]',
'task_specific',
'Template para lembrete de medicação'),

('eva_check_bem_estar', 'v2.0',
'TAREFA ATUAL: Check-in de Bem-Estar

OBJETIVO: Avaliar estado emocional e físico de {{nome_idoso}}

PERGUNTAS SUGERIDAS (adapte naturalmente):
1. Como você está se sentindo hoje?
2. Dormiu bem esta noite?
3. Já comeu algo hoje? Como está o apetite?
4. Está sentindo alguma dor ou desconforto?
5. Fez alguma atividade que gosta hoje?

SINAIS DE ALERTA:
- Tristeza ou apatia profunda → Registre via register_sentiment
- Dor persistente ou nova → alert_family urgência "média"
- Confusão mental ou desorientação → alert_family urgência "alta"
- Não comeu há mais de 24h → alert_family urgência "alta"
- Quedas ou acidentes → alert_family urgência "crítica"

ENCERRAMENTO:
- Sempre termine com uma mensagem positiva
- Confirme que pode ligar novamente se precisar
- Lembre do próximo horário de contato',
'[]',
'task_specific',
'Template para check-in de bem-estar'),

('eva_recovery_conexao', 'v2.0',
'SITUAÇÃO: Reconexão após queda de conexão

"Oi {{nome_idoso}}, desculpe, nossa ligação caiu por um momento. {{ultima_interacao_contexto}}. Podemos continuar de onde paramos?"

ÚLTIMO ESTADO: {{ultima_interacao_estado}}

Continue naturalmente a partir daqui, não repita informações já confirmadas.',
'["ultima_interacao_contexto", "ultima_interacao_estado"]',
'recovery',
'Template para reconexão após queda');

-- ================================================================
-- TABELA 3: function_definitions
-- Definições de funções para Function Calling
-- ================================================================
CREATE TABLE function_definitions (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) UNIQUE NOT NULL,
    descricao TEXT NOT NULL,
    parametros JSONB NOT NULL,
    tipo_tarefa VARCHAR(50) NOT NULL,
    handler_path VARCHAR(255) NOT NULL,
    validations JSONB DEFAULT '{}',
    requires_confirmation BOOLEAN DEFAULT false,
    max_executions_per_call INTEGER DEFAULT 1,
    ativa BOOLEAN DEFAULT true,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_function_nome ON function_definitions(nome) WHERE ativa = true;
CREATE INDEX idx_function_tipo ON function_definitions(tipo_tarefa) WHERE ativa = true;

CREATE TRIGGER trigger_function_timestamp
BEFORE UPDATE ON function_definitions
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- ================================================================
-- DADOS INICIAIS: function_definitions
-- ================================================================
INSERT INTO function_definitions (nome, descricao, parametros, tipo_tarefa, handler_path, validations) VALUES
('confirm_medication', 
'Confirma se o idoso tomou o medicamento prescrito. Use esta função após conversar sobre a medicação.',
'{
  "type": "object",
  "properties": {
    "medicamento": {
      "type": "string",
      "description": "Nome do medicamento confirmado"
    },
    "tomou": {
      "type": "boolean",
      "description": "true se o idoso tomou, false se não tomou"
    },
    "horario_real": {
      "type": "string",
      "description": "Horário aproximado que tomou (ex: há 1 hora, de manhã)",
      "nullable": true
    },
    "observacoes": {
      "type": "string",
      "description": "Qualquer observação relevante (efeitos colaterais, dificuldade em engolir, etc.)",
      "nullable": true
    }
  },
  "required": ["medicamento", "tomou"]
}',
'lembrete_medicamento',
'handlers.medication.confirm_medication',
'{
  "allowed_operations": ["read", "confirm"],
  "requires_human_approval": false,
  "max_execution_time_seconds": 5,
  "safety_check": "validate_medication_exists"
}'),

('register_sentiment',
'Registra o estado emocional/humor do idoso durante a conversa. Use quando perceber mudanças de humor significativas.',
'{
  "type": "object",
  "properties": {
    "sentimento": {
      "type": "string",
      "enum": ["feliz", "triste", "ansioso", "irritado", "confuso", "apatico", "animado"],
      "description": "Sentimento predominante detectado"
    },
    "intensidade": {
      "type": "string",
      "enum": ["leve", "moderada", "intensa"],
      "description": "Intensidade do sentimento"
    },
    "contexto": {
      "type": "string",
      "description": "Breve contexto do que provocou este sentimento"
    }
  },
  "required": ["sentimento", "intensidade"]
}',
'check_bem_estar',
'handlers.sentiment.register_sentiment',
'{
  "allowed_operations": ["create"],
  "requires_human_approval": false,
  "max_execution_time_seconds": 3
}'),

('alert_family',
'FUNÇÃO DE EMERGÊNCIA: Envia alerta imediato para familiares. Use apenas em situações que exigem atenção urgente.',
'{
  "type": "object",
  "properties": {
    "motivo": {
      "type": "string",
      "description": "Descrição clara do motivo do alerta"
    },
    "urgencia": {
      "type": "string",
      "enum": ["baixa", "média", "alta", "crítica"],
      "description": "Nível de urgência: baixa (pode esperar 24h), média (atenção no dia), alta (atenção em 1-2h), crítica (IMEDIATO)"
    },
    "categoria": {
      "type": "string",
      "enum": ["medicamento", "saude_fisica", "saude_mental", "seguranca", "outro"],
      "description": "Categoria do alerta"
    }
  },
  "required": ["motivo", "urgencia", "categoria"]
}',
'all',
'handlers.alerts.alert_family',
'{
  "allowed_operations": ["create"],
  "requires_human_approval": false,
  "max_execution_time_seconds": 10,
  "rate_limit": "5_per_hour"
}'),

('schedule_callback',
'Agenda uma ligação de retorno para horário específico solicitado pelo idoso.',
'{
  "type": "object",
  "properties": {
    "horario_preferido": {
      "type": "string",
      "description": "Horário solicitado (formato: HH:MM ou descrição como tarde, noite)"
    },
    "motivo": {
      "type": "string",
      "description": "Motivo da ligação de retorno"
    }
  },
  "required": ["horario_preferido", "motivo"]
}',
'all',
'handlers.scheduling.schedule_callback',
'{
  "allowed_operations": ["create"],
  "requires_human_approval": true,
  "max_execution_time_seconds": 3
}');

-- ================================================================
-- TABELA 4: idosos
-- ================================================================
CREATE TABLE idosos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    data_nascimento DATE NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    foto_url TEXT,                      -- RECURSO: Foto do Idoso
    intro_audio_url TEXT,               -- RECURSO: Intro de Voz Familiar
    
    -- Perfil de Saúde
    nivel_cognitivo VARCHAR(50) DEFAULT 'normal' CHECK (nivel_cognitivo IN ('normal', 'leve', 'moderado', 'severo')),
    limitacoes_auditivas BOOLEAN DEFAULT false,
    usa_aparelho_auditivo BOOLEAN DEFAULT false,
    limitacoes_visuais BOOLEAN DEFAULT false,
    mobilidade VARCHAR(50) DEFAULT 'independente' CHECK (mobilidade IN ('independente', 'auxiliado', 'cadeira_rodas', 'acamado')),
    
    -- Personalização
    tom_voz VARCHAR(50) DEFAULT 'amigavel' CHECK (tom_voz IN ('formal', 'amigavel', 'maternal', 'jovial')),
    preferencia_horario_ligacao VARCHAR(50) DEFAULT 'manha' CHECK (preferencia_horario_ligacao IN ('manha', 'tarde', 'noite', 'qualquer')),
    timezone VARCHAR(50) DEFAULT 'America/Sao_Paulo',
    
    -- Ajustes Técnicos de Áudio
    ganho_audio_entrada INTEGER DEFAULT 0 CHECK (ganho_audio_entrada BETWEEN -5 AND 5),
    ganho_audio_saida INTEGER DEFAULT 0 CHECK (ganho_audio_saida BETWEEN -5 AND 5),
    ambiente_ruidoso BOOLEAN DEFAULT false,
    
    -- Contatos de Emergência
    familiar_principal JSONB NOT NULL DEFAULT '{"nome": "", "telefone": "", "parentesco": ""}',
    contato_emergencia JSONB DEFAULT '{"nome": "", "telefone": "", "parentesco": ""}',
    medico_responsavel JSONB DEFAULT '{"nome": "", "telefone": "", "crm": ""}',
    
    -- Medicamentos Atuais
    medicamentos_atuais JSONB DEFAULT '[]',
    condicoes_medicas TEXT,
    
    -- Estado Emocional e Tracking (Frontend)
    sentimento VARCHAR(50) DEFAULT 'neutro' CHECK (sentimento IN ('feliz', 'neutro', 'triste', 'ansioso', 'irritado', 'confuso', 'apatico')),
    agendamentos_pendentes INTEGER DEFAULT 0,
    
    -- Metadata
    notas_gerais TEXT,
    ativo BOOLEAN DEFAULT true,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_idade CHECK (EXTRACT(YEAR FROM AGE(data_nascimento)) >= 0)
);

-- ================================================================
-- TABELA 4.1: membros_familia (NOVA)
-- Para Árvore Genealógica e Responsáveis
-- ================================================================
CREATE TABLE membros_familia (
    id SERIAL PRIMARY KEY,
    idoso_id INTEGER NOT NULL REFERENCES idosos(id) ON DELETE CASCADE,
    parent_id INTEGER REFERENCES membros_familia(id), -- Auto-relacionamento para Árvore
    nome VARCHAR(255) NOT NULL,
    parentesco VARCHAR(100) NOT NULL,
    foto_url TEXT,
    is_responsavel BOOLEAN DEFAULT false,
    telefone VARCHAR(20),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_familia_idoso ON membros_familia(idoso_id);

CREATE TRIGGER trigger_familia_timestamp
BEFORE UPDATE ON membros_familia
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE INDEX idx_idoso_telefone ON idosos(telefone) WHERE ativo = true;
CREATE INDEX idx_idoso_ativo ON idosos(ativo);

CREATE TRIGGER trigger_idoso_timestamp
BEFORE UPDATE ON idosos
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- ================================================================
-- TABELA 5: agendamentos
-- ================================================================
CREATE TABLE agendamentos (
    id SERIAL PRIMARY KEY,
    idoso_id INTEGER NOT NULL REFERENCES idosos(id) ON DELETE CASCADE,
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('lembrete_medicamento', 'check_bem_estar', 'acompanhamento_pos_consulta', 'atividade_fisica')),
    
    -- Scheduling
    data_hora_agendada TIMESTAMP NOT NULL,
    data_hora_realizada TIMESTAMP,
    
    -- Retry Policy
    max_retries INTEGER DEFAULT 3,
    retry_interval_minutes INTEGER DEFAULT 15,
    tentativas_realizadas INTEGER DEFAULT 0,
    proxima_tentativa TIMESTAMP,
    escalation_policy VARCHAR(50) DEFAULT 'alert_family' CHECK (escalation_policy IN ('alert_family', 'emergency_contact', 'none')),
    
    -- Estado da Ligação
    status VARCHAR(50) DEFAULT 'agendado' CHECK (status IN (
        'agendado', 
        'em_andamento', 
        'concluido', 
        'falhou', 
        'aguardando_retry',
        'falhou_definitivamente',
        'cancelado'
    )),
    
    -- Session Management (para reconexão)
    gemini_session_handle VARCHAR(255),
    ultima_interacao_estado JSONB,
    session_expires_at TIMESTAMP,
    
    -- Dados Específicos da Tarefa
    dados_tarefa JSONB NOT NULL DEFAULT '{}',
    prioridade VARCHAR(10) DEFAULT 'normal' CHECK (prioridade IN ('alta', 'normal', 'baixa')),
    
    -- Metadata
    criado_por VARCHAR(100) DEFAULT 'sistema',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_agendamento_idoso ON agendamentos(idoso_id);
CREATE INDEX idx_agendamento_data ON agendamentos(data_hora_agendada);
CREATE INDEX idx_agendamento_status ON agendamentos(status);
CREATE INDEX idx_agendamento_proxima_tentativa ON agendamentos(proxima_tentativa) WHERE status = 'aguardando_retry';

CREATE TRIGGER trigger_agendamento_timestamp
BEFORE UPDATE ON agendamentos
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- ================================================================
-- TABELA 6: historico_ligacoes
-- ================================================================
CREATE TABLE historico_ligacoes (
    id SERIAL PRIMARY KEY,
    agendamento_id INTEGER NOT NULL REFERENCES agendamentos(id) ON DELETE CASCADE,
    idoso_id INTEGER NOT NULL REFERENCES idosos(id) ON DELETE CASCADE,
    
    -- Identificadores Técnicos
    twilio_call_sid VARCHAR(255),
    stream_sid VARCHAR(255),
    
    -- Timestamps
    inicio_chamada TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fim_chamada TIMESTAMP,
    duracao_segundos INTEGER,
    
    -- Configurações Utilizadas (snapshot)
    modelo_utilizado VARCHAR(100),
    voice_name VARCHAR(50),
    config_snapshot JSONB,
    
    -- Telemetria de Qualidade
    qualidade_audio VARCHAR(50) CHECK (qualidade_audio IN ('excelente', 'boa', 'regular', 'ruim')),
    interrupcoes_detectadas INTEGER DEFAULT 0,
    latencia_media_ms INTEGER,
    packets_perdidos INTEGER DEFAULT 0,
    vad_false_positives INTEGER DEFAULT 0,
    
    -- Resultado da Ligação
    tarefa_concluida BOOLEAN DEFAULT false,
    objetivo_alcancado BOOLEAN,
    motivo_falha TEXT,
    
    -- Transcrição e Análise
    transcricao_completa TEXT,
    transcricao_resumo TEXT,
    sentimento_geral VARCHAR(50),
    sentimento_intensidade INTEGER CHECK (sentimento_intensidade BETWEEN 1 AND 10),
    acoes_registradas JSONB DEFAULT '[]',
    
    -- Métricas de Custo (FinOps)
    tokens_gemini INTEGER DEFAULT 0,    -- RECURSO: FinOps
    minutos_twilio INTEGER DEFAULT 0,    -- RECURSO: FinOps
    
    -- Metadata
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_historico_agendamento ON historico_ligacoes(agendamento_id);
CREATE INDEX idx_historico_idoso ON historico_ligacoes(idoso_id);
CREATE INDEX idx_historico_data ON historico_ligacoes(inicio_chamada);
CREATE INDEX idx_historico_call_sid ON historico_ligacoes(twilio_call_sid);

-- ================================================================
-- TABELA 7: alertas
-- ================================================================
CREATE TABLE alertas (
    id SERIAL PRIMARY KEY,
    idoso_id INTEGER NOT NULL REFERENCES idosos(id) ON DELETE CASCADE,
    ligacao_id INTEGER REFERENCES historico_ligacoes(id) ON DELETE SET NULL,
    
    -- Tipo e Severidade
    tipo VARCHAR(100) NOT NULL CHECK (tipo IN (
        'dose_esquecida',
        'efeito_colateral',
        'queda',
        'confusao_mental',
        'tristeza_profunda',
        'dor_intensa',
        'nao_atende_telefone',
        'alerta_ia',
        'outro'
    )),
    severidade VARCHAR(50) NOT NULL CHECK (severidade IN ('baixa', 'aviso', 'alta', 'critica')),
    
    -- Mensagem
    mensagem TEXT NOT NULL,
    contexto_adicional JSONB DEFAULT '{}',
    
    -- Destinatários
    destinatarios JSONB NOT NULL,
    
    -- Status
    enviado BOOLEAN DEFAULT false,
    data_envio TIMESTAMP,
    visualizado BOOLEAN DEFAULT false,
    data_visualizacao TIMESTAMP,
    resolvido BOOLEAN DEFAULT false,
    data_resolucao TIMESTAMP,
    resolucao_nota TEXT,
    
    -- Metadata
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_alerta_idoso ON alertas(idoso_id);
CREATE INDEX idx_alerta_severidade ON alertas(severidade) WHERE NOT resolvido;
CREATE INDEX idx_alerta_enviado ON alertas(enviado);
CREATE INDEX idx_alerta_resolvido ON alertas(resolvido);

-- ================================================================
-- TABELA 7.1: protocolos_alerta (NOVA)
-- Configuração do Orquestrador de Fluxos
-- ================================================================
CREATE TABLE protocolos_alerta (
    id SERIAL PRIMARY KEY,
    idoso_id INTEGER NOT NULL REFERENCES idosos(id) ON DELETE CASCADE,
    nome VARCHAR(100) DEFAULT 'Protocolo Padrão',
    ativo BOOLEAN DEFAULT true,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE protocolo_etapas (
    id SERIAL PRIMARY KEY,
    protocolo_id INTEGER NOT NULL REFERENCES protocolos_alerta(id) ON DELETE CASCADE,
    ordem INTEGER NOT NULL,
    acao VARCHAR(50) NOT NULL, -- RETRY, NOTIFY_WA, NOTIFY_SMS
    delay_minutos INTEGER DEFAULT 5,
    tentativas INTEGER DEFAULT 1,
    contato_alvo VARCHAR(255),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER trigger_protocolo_timestamp
BEFORE UPDATE ON protocolos_alerta
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- ================================================================
-- TABELA 8: medicamentos (NOVA)
-- Catálogo de medicamentos por idoso
-- ================================================================
CREATE TABLE medicamentos (
    id SERIAL PRIMARY KEY,
    idoso_id INTEGER NOT NULL REFERENCES idosos(id) ON DELETE CASCADE,
    nome VARCHAR(255) NOT NULL,
    principio_ativo VARCHAR(255),
    dosagem VARCHAR(100),
    forma VARCHAR(50) CHECK (forma IN ('comprimido', 'capsula', 'liquido', 'injetavel', 'pomada', 'outro')),
    horarios JSONB DEFAULT '[]',
    observacoes TEXT,
    ativo BOOLEAN DEFAULT true,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_medicamento_idoso ON medicamentos(idoso_id) WHERE ativo = true;
CREATE INDEX idx_medicamento_nome ON medicamentos(nome);

CREATE TRIGGER trigger_medicamento_timestamp
BEFORE UPDATE ON medicamentos
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- ================================================================
-- TABELA 9: idosos_memoria (NOVA)
-- Fatos biográficos para personalização da EVA
-- ================================================================
CREATE TABLE idosos_memoria (
    id SERIAL PRIMARY KEY,
    idoso_id INTEGER NOT NULL REFERENCES idosos(id) ON DELETE CASCADE,
    categoria VARCHAR(100) NOT NULL, -- Família, Hobbies, Profissão, etc.
    chave VARCHAR(255) NOT NULL,    -- Ex: "Neto Preferido"
    valor TEXT NOT NULL,           -- Ex: "Joãozinho"
    relevancia VARCHAR(20) DEFAULT 'media' CHECK (relevancia IN ('baixa', 'media', 'alta')),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_memoria_idoso ON idosos_memoria(idoso_id);

CREATE TRIGGER trigger_memoria_timestamp
BEFORE UPDATE ON idosos_memoria
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- ================================================================
-- TABELA 10: idosos_perfil_clinico (NOVA)
-- Dados médicos críticos para emergências
-- ================================================================
CREATE TABLE idosos_perfil_clinico (
    idoso_id INTEGER PRIMARY KEY REFERENCES idosos(id) ON DELETE CASCADE,
    tipo_sanguineo VARCHAR(5) CHECK (tipo_sanguineo IN ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-')),
    alergias TEXT,
    restricoes_locomocao TEXT,
    doencas_cronicas TEXT,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER trigger_perfil_clinico_timestamp
BEFORE UPDATE ON idosos_perfil_clinico
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- ================================================================
-- TABELA 11: assinaturas_entidade (NOVA)
-- Controle de faturamento e limites Enterprise
-- ================================================================
CREATE TABLE assinaturas_entidade (
    id SERIAL PRIMARY KEY,
    entidade_nome VARCHAR(255) NOT NULL, -- Nome da clínica ou responsável
    status VARCHAR(50) DEFAULT 'ativo' CHECK (status IN ('ativo', 'cancelado', 'pendente', 'suspenso')),
    plano_id VARCHAR(50) NOT NULL,         -- Ex: 'enterprise_v1'
    data_proxima_cobranca DATE,
    limite_minutos INTEGER DEFAULT 1000,
    minutos_consumidos INTEGER DEFAULT 0,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER trigger_assinatura_timestamp
BEFORE UPDATE ON assinaturas_entidade
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- ================================================================
-- TABELA 12: faturamento_consumo (NOVA)
-- Dados para FinOps Dashboard
-- ================================================================
CREATE TABLE faturamento_consumo (
    id SERIAL PRIMARY KEY,
    idoso_id INTEGER REFERENCES idosos(id) ON DELETE CASCADE,
    mes_referencia INTEGER NOT NULL,
    ano_referencia INTEGER NOT NULL,
    total_tokens INTEGER DEFAULT 0,
    total_minutos INTEGER DEFAULT 0,
    custo_total_estimado DECIMAL(10,2) DEFAULT 0.00,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ================================================================
-- TABELA 13: audit_logs (NOVA)
-- Sistema de Auditoria Completo
-- ================================================================
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    usuario_email VARCHAR(255),
    acao VARCHAR(100) NOT NULL,
    recurso VARCHAR(255),
    detalhes TEXT,
    ip_address VARCHAR(45),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_acao ON audit_logs(acao);
CREATE INDEX idx_audit_usuario ON audit_logs(usuario_email);

-- ================================================================
-- VIEWS ÚTEIS
-- ================================================================

-- View: Próximas ligações agendadas
CREATE VIEW v_proximas_ligacoes AS
SELECT 
    a.id,
    a.data_hora_agendada,
    a.tipo,
    a.status,
    a.tentativas_realizadas,
    i.nome as idoso_nome,
    i.telefone,
    i.timezone,
    EXTRACT(YEAR FROM AGE(i.data_nascimento)) as idade,
    i.limitacoes_auditivas,
    i.usa_aparelho_auditivo
FROM agendamentos a
JOIN idosos i ON a.idoso_id = i.id
WHERE a.status IN ('agendado', 'aguardando_retry')
    AND a.data_hora_agendada >= CURRENT_TIMESTAMP
    AND i.ativo = true
ORDER BY a.data_hora_agendada;

-- View: Taxa de adesão por idoso
CREATE VIEW v_taxa_adesao_idoso AS
SELECT 
    i.id as idoso_id,
    i.nome,
    COUNT(h.id) as total_ligacoes,
    COUNT(CASE WHEN h.tarefa_concluida THEN 1 END) as ligacoes_bem_sucedidas,
    ROUND(
        100.0 * COUNT(CASE WHEN h.tarefa_concluida THEN 1 END) / NULLIF(COUNT(h.id), 0),
        2
    ) as taxa_adesao_pct,
    MAX(h.inicio_chamada) as ultima_ligacao
FROM idosos i
LEFT JOIN historico_ligacoes h ON i.id = h.idoso_id
WHERE i.ativo = true
GROUP BY i.id, i.nome;

-- View: Alertas pendentes por severidade
CREATE VIEW v_alertas_pendentes AS
SELECT 
    a.id,
    a.idoso_id,
    i.nome as idoso_nome,
    a.tipo,
    a.severidade,
    a.mensagem,
    a.criado_em,
    EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - a.criado_em))/3600 as horas_aberto,
    a.enviado,
    a.visualizado
FROM alertas a
JOIN idosos i ON a.idoso_id = i.id
WHERE NOT a.resolvido
ORDER BY 
    CASE a.severidade 
        WHEN 'critica' THEN 1
        WHEN 'alta' THEN 2
        WHEN 'aviso' THEN 3
        WHEN 'baixa' THEN 4
    END,
    a.criado_em;

-- View: Métricas de qualidade técnica
CREATE VIEW v_metricas_qualidade AS
SELECT 
    DATE(h.inicio_chamada) as data,
    COUNT(*) as total_ligacoes,
    AVG(h.duracao_segundos) as duracao_media_seg,
    AVG(h.latencia_media_ms) as latencia_media_ms,
    AVG(h.interrupcoes_detectadas) as interrupcoes_media,
    AVG(h.vad_false_positives) as falsos_positivos_media,
    COUNT(CASE WHEN h.qualidade_audio IN ('excelente', 'boa') THEN 1 END) as ligacoes_boa_qualidade,
    ROUND(
        100.0 * COUNT(CASE WHEN h.qualidade_audio IN ('excelente', 'boa') THEN 1 END) / COUNT(*),
        2
    ) as pct_boa_qualidade
FROM historico_ligacoes h
WHERE h.fim_chamada IS NOT NULL
GROUP BY DATE(h.inicio_chamada)
ORDER BY data DESC;

-- ================================================================
-- FUNÇÕES AUXILIARES
-- ================================================================

-- Função: Calcula próxima tentativa de ligação
CREATE OR REPLACE FUNCTION calcular_proxima_tentativa(
    p_agendamento_id INTEGER,
    p_intervalo_minutos INTEGER DEFAULT 15
)
RETURNS TIMESTAMP AS $$
DECLARE
    v_proxima TIMESTAMP;
BEGIN
    v_proxima := CURRENT_TIMESTAMP + (p_intervalo_minutos || ' minutes')::INTERVAL;
    
    UPDATE agendamentos
    SET proxima_tentativa = v_proxima,
        status = 'aguardando_retry'
    WHERE id = p_agendamento_id;
    
    RETURN v_proxima;
END;
$$ LANGUAGE plpgsql;

-- Função: Busca configuração do sistema
CREATE OR REPLACE FUNCTION get_config(p_chave VARCHAR)
RETURNS TEXT AS $$
DECLARE
    v_valor TEXT;
BEGIN
    SELECT valor INTO v_valor
    FROM configuracoes_sistema
    WHERE chave = p_chave AND ativa = true
    LIMIT 1;
    
    RETURN v_valor;
END;
$$ LANGUAGE plpgsql;

-- Função: Busca configuração tipada
CREATE OR REPLACE FUNCTION get_config_int(p_chave VARCHAR, p_default INTEGER DEFAULT 0)
RETURNS INTEGER AS $$
DECLARE
    v_valor TEXT;
BEGIN
    v_valor := get_config(p_chave);
    IF v_valor IS NULL THEN
        RETURN p_default;
    END IF;
    RETURN v_valor::INTEGER;
EXCEPTION WHEN OTHERS THEN
    RETURN p_default;
END;
$$ LANGUAGE plpgsql;

-- ================================================================
-- TABELA 14: idosos_legado_digital (NOVA)
-- Cápsula do tempo para familiares
-- ================================================================
CREATE TABLE idosos_legado_digital (
    id SERIAL PRIMARY KEY,
    idoso_id INTEGER NOT NULL REFERENCES idosos(id) ON DELETE CASCADE,
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('audio', 'video', 'imagem', 'carta')),
    titulo VARCHAR(255) NOT NULL,
    url_midia TEXT NOT NULL, 
    destinatario VARCHAR(255),
    protegido BOOLEAN DEFAULT true,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ================================================================
-- TABELA 15: psicologia_insights (NOVA)
-- Insights gerados pela Psicóloga IA
-- ================================================================
CREATE TABLE psicologia_insights (
    id SERIAL PRIMARY KEY,
    idoso_id INTEGER NOT NULL REFERENCES idosos(id) ON DELETE CASCADE,
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('positivo', 'alerta', 'vincular', 'evolucao')),
    mensagem TEXT NOT NULL,
    data_insight TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    relevancia VARCHAR(20) DEFAULT 'media'
);

-- ================================================================
-- TABELA 16: topicos_afetivos (NOVA)
-- Nuvem de Tópicos e Frequência de Menções
-- ================================================================
CREATE TABLE topicos_afetivos (
    id SERIAL PRIMARY KEY,
    idoso_id INTEGER NOT NULL REFERENCES idosos(id) ON DELETE CASCADE,
    topico VARCHAR(100) NOT NULL,
    frequencia INTEGER DEFAULT 1,
    sentimento_associado VARCHAR(50),
    ultima_mencao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ================================================================
-- TABELA 17: sinais_vitais (NOVA)
-- Monitoramento de Saúde via Voz/Conversa
-- ================================================================
CREATE TABLE sinais_vitais (
    id SERIAL PRIMARY KEY,
    idoso_id INTEGER NOT NULL REFERENCES idosos(id) ON DELETE CASCADE,
    tipo VARCHAR(100) NOT NULL, -- 'pressao_arterial', 'glicose', 'temperatura'
    valor VARCHAR(50) NOT NULL,
    unidade VARCHAR(20),
    metodo VARCHAR(50) DEFAULT 'voz_ia',
    data_medicao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ================================================================
-- FIM DO SCHEMA v6.0
-- ================================================================