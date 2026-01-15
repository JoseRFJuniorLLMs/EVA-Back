-- =====================================================
-- EVA-back: Payment Tables Migration (Wise Integration)
-- Descrição: Tabelas para Assinaturas, Transações e Wise
-- =====================================================

-- 1. Subscriptions Table
CREATE TABLE IF NOT EXISTS subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES usuarios(id),
    plan_tier VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    payment_method_default VARCHAR(50),
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    metadata_json JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. Transactions Table
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES usuarios(id),
    amount DECIMAL(10, 2),
    currency VARCHAR(3),
    provider VARCHAR(50),
    status VARCHAR(20),
    external_ref VARCHAR(255) UNIQUE,
    failure_reason VARCHAR(255),
    proof_url VARCHAR(500),
    subscription_id INTEGER REFERENCES subscriptions(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 3. Wise Payment References Table
CREATE TABLE IF NOT EXISTS wise_payment_references (
    id SERIAL PRIMARY KEY,
    reference_code VARCHAR(50) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES usuarios(id),
    subscription_id INTEGER REFERENCES subscriptions(id),
    expected_amount DECIMAL(10, 2) NOT NULL,
    expected_currency VARCHAR(3) NOT NULL,
    plan_tier VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP,
    metadata_json JSONB DEFAULT '{}'
);

-- Índices e Otimizações
CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON subscriptions(user_id);

CREATE UNIQUE INDEX IF NOT EXISTS idx_wise_reference_code ON wise_payment_references(reference_code);
CREATE INDEX IF NOT EXISTS idx_wise_user_status ON wise_payment_references(user_id, status);
CREATE INDEX IF NOT EXISTS idx_wise_expires ON wise_payment_references(expires_at) WHERE status = 'pending';

-- Trigger para updated_at em subscriptions e transactions
CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON subscriptions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON transactions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
