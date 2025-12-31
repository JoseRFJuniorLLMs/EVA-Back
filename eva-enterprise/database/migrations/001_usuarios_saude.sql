-- =====================================================
-- EVA-back: Health Data Tables Migration
-- Criado em: 2025-12-31
-- Descrição: Tabelas para monitoramento de saúde e bem-estar
-- =====================================================

-- 1. Tabela de Usuários (Base para o cliente_id)
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    matricula VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 2. Atividade Física
CREATE TABLE IF NOT EXISTS atividade (
    id BIGSERIAL PRIMARY KEY,
    cliente_id INT REFERENCES usuarios(id) ON DELETE CASCADE,
    passos INT DEFAULT 0,
    calorias_queimadas NUMERIC(10, 2),
    distancia_km NUMERIC(10, 2),
    andares_subidos INT,
    velocidade_media NUMERIC(5, 2),
    cadencia_pedalada INT,
    potencia_watts INT,
    tipo_exercicio VARCHAR(100), -- Ex: corrida, natação, ciclismo
    timestamp_coleta TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 3. Sinais Vitais (renomeado para evitar conflito com tabela existente)
CREATE TABLE IF NOT EXISTS sinais_vitais_health (
    id BIGSERIAL PRIMARY KEY,
    cliente_id INT REFERENCES usuarios(id) ON DELETE CASCADE,
    bpm INT,
    bpm_repouso INT,
    pressao_sistolica INT, -- Ex: 120
    pressao_diastolica INT, -- Ex: 80
    spo2 NUMERIC(5, 2), -- Saturação de Oxigênio (0-100)
    glicose_sangue NUMERIC(10, 2),
    frequencia_respiratoria INT,
    timestamp_coleta TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 4. Sono
CREATE TABLE IF NOT EXISTS sono (
    id BIGSERIAL PRIMARY KEY,
    cliente_id INT REFERENCES usuarios(id) ON DELETE CASCADE,
    duracao_total_minutos INT,
    estagio_leve_minutos INT,
    estagio_profundo_minutos INT,
    estagio_rem_minutos INT,
    tempo_acordado_minutos INT,
    timestamp_inicio TIMESTAMPTZ,
    timestamp_fim TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 5. Medição Corporal
CREATE TABLE IF NOT EXISTS medicao_corporal (
    id BIGSERIAL PRIMARY KEY,
    cliente_id INT REFERENCES usuarios(id) ON DELETE CASCADE,
    peso_kg NUMERIC(5, 2),
    altura_cm NUMERIC(5, 2),
    perc_gordura_corporal NUMERIC(5, 2),
    massa_ossea_kg NUMERIC(5, 2),
    massa_magra_kg NUMERIC(5, 2),
    circunferencia_cintura_cm NUMERIC(5, 2),
    circunferencia_quadril_cm NUMERIC(5, 2),
    timestamp_coleta TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 6. Nutrição e Hidratação
CREATE TABLE IF NOT EXISTS nutricao (
    id BIGSERIAL PRIMARY KEY,
    cliente_id INT REFERENCES usuarios(id) ON DELETE CASCADE,
    ingestao_agua_ml INT,
    calorias_consumidas INT,
    proteinas_g NUMERIC(10, 2),
    carboidratos_g NUMERIC(10, 2),
    gorduras_g NUMERIC(10, 2),
    vitaminas_json JSONB, -- Armazena detalhes de vitaminas em formato flexível
    timestamp_coleta TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 7. Ciclo Menstrual
CREATE TABLE IF NOT EXISTS ciclo_menstrual (
    id BIGSERIAL PRIMARY KEY,
    cliente_id INT REFERENCES usuarios(id) ON DELETE CASCADE,
    data_menstruacao DATE,
    teste_ovulacao VARCHAR(50), -- Positivo/Negativo
    muco_cervical VARCHAR(100),
    atividade_sexual BOOLEAN,
    sintomas_json JSONB, -- Sintomas adicionais em formato flexível
    timestamp_coleta TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- ÍNDICES PARA PERFORMANCE
-- =====================================================

-- Índices compostos para queries de histórico (cliente + timestamp)
CREATE INDEX IF NOT EXISTS idx_atividade_cliente_timestamp 
    ON atividade(cliente_id, timestamp_coleta DESC);

CREATE INDEX IF NOT EXISTS idx_sinais_vitais_health_cliente_timestamp 
    ON sinais_vitais_health(cliente_id, timestamp_coleta DESC);

CREATE INDEX IF NOT EXISTS idx_sono_cliente_timestamp 
    ON sono(cliente_id, timestamp_inicio DESC);

CREATE INDEX IF NOT EXISTS idx_medicao_corporal_cliente_timestamp 
    ON medicao_corporal(cliente_id, timestamp_coleta DESC);

CREATE INDEX IF NOT EXISTS idx_nutricao_cliente_timestamp 
    ON nutricao(cliente_id, timestamp_coleta DESC);

CREATE INDEX IF NOT EXISTS idx_ciclo_menstrual_cliente_data 
    ON ciclo_menstrual(cliente_id, data_menstruacao DESC);

-- Índice para busca por email de usuário
CREATE INDEX IF NOT EXISTS idx_usuarios_email 
    ON usuarios(email);

-- =====================================================
-- COMENTÁRIOS NAS TABELAS
-- =====================================================

COMMENT ON TABLE usuarios IS 'Usuários do sistema de monitoramento de saúde';
COMMENT ON TABLE atividade IS 'Registros de atividade física e exercícios';
COMMENT ON TABLE sinais_vitais_health IS 'Sinais vitais coletados de dispositivos de saúde';
COMMENT ON TABLE sono IS 'Registros de sessões de sono e qualidade';
COMMENT ON TABLE medicao_corporal IS 'Medições corporais e composição';
COMMENT ON TABLE nutricao IS 'Registros de nutrição e hidratação';
COMMENT ON TABLE ciclo_menstrual IS 'Registros do ciclo menstrual';

-- =====================================================
-- TRIGGER PARA ATUALIZAR updated_at
-- =====================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_usuarios_updated_at 
    BEFORE UPDATE ON usuarios 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- DADOS DE EXEMPLO (OPCIONAL - COMENTADO)
-- =====================================================

-- INSERT INTO usuarios (nome, email, matricula) VALUES
-- ('João Silva', 'joao@example.com', '12345'),
-- ('Maria Santos', 'maria@example.com', '67890');

-- INSERT INTO sinais_vitais_health (cliente_id, bpm, pressao_sistolica, pressao_diastolica, spo2, timestamp_coleta) VALUES
-- (1, 75, 120, 80, 98.5, '2025-12-31 09:00:00+00'),
-- (1, 72, 118, 78, 99.0, '2025-12-31 12:00:00+00');

-- INSERT INTO atividade (cliente_id, passos, calorias_queimadas, distancia_km, timestamp_coleta) VALUES
-- (1, 8500, 320.5, 6.2, '2025-12-31 20:00:00+00');
