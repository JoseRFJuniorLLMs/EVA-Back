# 📋 CHECKLIST COMPLETO: HUB FINANCEIRO EVA

## ANÁLISE DA ARQUITETURA ATUAL

### Projetos EVA Existentes:
1. **EVA-Mind** (Go) - WebSocket real-time, Gemini AI
2. **EVA-back** (Python/FastAPI) - API REST principal
3. **EVA-Voice** (Python/FastAPI) - Microserviço de voz (Coqui XTTS)
4. **EVA-Front** (Next.js) - Frontend web
5. **EVA-Mobile** (Flutter) - App mobile

### Banco de Dados Atual (PostgreSQL):
- ✅ Tabelas existentes: `usuarios`, `idosos`, `cuidadores`, `medicamentos`, `agendamentos`, `alertas`
- ✅ Sistema de saúde já implementado
- ✅ Autenticação com bcrypt
- ⚠️ **FALTA**: Sistema de pagamentos e assinaturas

---

## 1️⃣ CHECKLIST BACKEND PYTHON (EVA-back)

### Fase 1: Estrutura Base (Semana 1)
- [ ] **1.1** Criar diretório `api_financeiro/` dentro de `eva-enterprise/`
- [ ] **1.2** Configurar estrutura modular:
  ```
  eva-enterprise/
  ├── api/
  │   ├── routes_checkout.py      # ← NOVO
  │   ├── routes_webhooks.py      # ← NOVO
  │   ├── routes_subscriptions.py # ← NOVO
  │   └── routes_admin_payments.py # ← NOVO
  ├── services/
  │   ├── payment/
  │   │   ├── stripe_service.py   # ← NOVO
  │   │   ├── asaas_service.py    # ← NOVO
  │   │   ├── opennode_service.py # ← NOVO
  │   │   └── wise_service.py     # ← NOVO
  │   └── storage_service.py      # ← NOVO (GCS)
  └── schemas/
      ├── checkout.py             # ← NOVO
      ├── webhook.py              # ← NOVO
      └── subscription.py         # ← NOVO
  ```

- [ ] **1.3** Adicionar dependências ao `requirements.txt`:
  ```txt
  stripe==10.12.0
  google-cloud-storage==2.14.0
  celery[redis]==5.3.4
  ```

- [ ] **1.4** Configurar variáveis de ambiente no `.env`:
  ```bash
  # Payment Gateways
  STRIPE_SECRET_KEY=sk_test_...
  STRIPE_WEBHOOK_SECRET=whsec_...
  ASAAS_API_KEY=...
  OPENNODE_API_KEY=...
  
  # Google Cloud
  GCP_PROJECT_ID=eva-project
  GCS_BUCKET_NAME=eva-receipts
  GOOGLE_APPLICATION_CREDENTIALS=path/to/key.json
  ```

### Fase 2: Schemas Pydantic (Semana 1)
- [ ] **2.1** Criar `schemas/checkout.py`:
  - [ ] `StripeCheckoutRequest`
  - [ ] `AsaasPixRequest`
  - [ ] `BitcoinInvoiceRequest`
  - [ ] `WiseInstructionsRequest`

- [ ] **2.2** Criar `schemas/subscription.py`:
  - [ ] `SubscriptionCreate`
  - [ ] `SubscriptionUpdate`
  - [ ] `SubscriptionResponse`

- [ ] **2.3** Criar `schemas/webhook.py`:
  - [ ] `StripeWebhookEvent`
  - [ ] `AsaasWebhookEvent`
  - [ ] `OpenNodeWebhookEvent`

### Fase 3: Services (Payment Gateways) (Semana 2-3)
- [ ] **3.1** Implementar `services/payment/stripe_service.py`:
  - [ ] `create_checkout_session()` - Criar sessão Stripe
  - [ ] `handle_webhook()` - Processar webhooks
  - [ ] `cancel_subscription()` - Cancelar assinatura
  - [ ] `get_customer()` - Buscar cliente

- [ ] **3.2** Implementar `services/payment/asaas_service.py`:
  - [ ] `create_pix_charge()` - Gerar QR Code Pix
  - [ ] `verify_payment()` - Verificar pagamento
  - [ ] `handle_webhook()` - Processar webhook Asaas

- [ ] **3.3** Implementar `services/payment/opennode_service.py`:
  - [ ] `create_lightning_invoice()` - Criar invoice Lightning
  - [ ] `convert_brl_to_btc()` - Conversão via Coingecko
  - [ ] `handle_webhook()` - Processar webhook Bitcoin

- [ ] **3.4** Implementar `services/payment/wise_service.py`:
  - [ ] `get_bank_instructions()` - Retornar dados bancários
  - [ ] `verify_transfer()` - Verificação manual

- [ ] **3.5** Implementar `services/storage_service.py` (GCS):
  - [ ] `upload_receipt()` - Upload de comprovante
  - [ ] `generate_signed_url()` - URL temporária
  - [ ] `delete_receipt()` - Remover arquivo

### Fase 4: Rotas API (Semana 3-4)
- [ ] **4.1** Criar `api/routes_checkout.py`:
  - [ ] `POST /api/v1/checkout/stripe-session`
  - [ ] `POST /api/v1/checkout/asaas-pix`
  - [ ] `POST /api/v1/checkout/bitcoin`
  - [ ] `GET /api/v1/checkout/instructions/{provider}`
  - [ ] `POST /api/v1/checkout/upload-receipt`

- [ ] **4.2** Criar `api/routes_webhooks.py`:
  - [ ] `POST /api/v1/webhooks/stripe`
  - [ ] `POST /api/v1/webhooks/asaas`
  - [ ] `POST /api/v1/webhooks/opennode`

- [ ] **4.3** Criar `api/routes_subscriptions.py`:
  - [ ] `GET /api/v1/subscriptions/me` - Minha assinatura
  - [ ] `GET /api/v1/subscriptions/{id}` - Detalhes
  - [ ] `POST /api/v1/subscriptions/cancel` - Cancelar
  - [ ] `GET /api/v1/subscriptions/history` - Histórico

- [ ] **4.4** Criar `api/routes_admin_payments.py`:
  - [ ] `GET /api/v1/admin/pending-receipts` - Comprovantes pendentes
  - [ ] `POST /api/v1/admin/approve-transaction/{id}` - Aprovar
  - [ ] `POST /api/v1/admin/reject-transaction/{id}` - Rejeitar
  - [ ] `GET /api/v1/admin/transactions` - Listar transações

- [ ] **4.5** Integrar rotas no `main.py`:
  ```python
  from api import (
      routes_checkout,
      routes_webhooks,
      routes_subscriptions,
      routes_admin_payments
  )
  
  app.include_router(routes_checkout.router, prefix="/api/v1", tags=["Checkout"])
  app.include_router(routes_webhooks.router, prefix="/api/v1", tags=["Webhooks"])
  app.include_router(routes_subscriptions.router, prefix="/api/v1", tags=["Subscriptions"])
  app.include_router(routes_admin_payments.router, prefix="/api/v1/admin", tags=["Admin Payments"])
  ```

### Fase 5: Celery Tasks (Semana 4)
- [ ] **5.1** Configurar Celery no `core/celery_app.py`
- [ ] **5.2** Criar tasks:
  - [ ] `process_stripe_webhook.delay()` - Processar webhook async
  - [ ] `check_expired_subscriptions()` - Cron diário
  - [ ] `send_renewal_reminder()` - Lembrete de renovação
  - [ ] `generate_monthly_report()` - Relatório mensal

### Fase 6: Segurança (Semana 5)
- [ ] **6.1** Implementar validação de webhooks (HMAC)
- [ ] **6.2** Rate limiting em endpoints de checkout
- [ ] **6.3** Validação de arquivos (upload):
  - [ ] Tipo MIME (image/jpeg, image/png, application/pdf)
  - [ ] Tamanho máximo (5MB)
  - [ ] Scan de vírus (opcional: ClamAV)

- [ ] **6.4** Criptografia de dados sensíveis:
  - [ ] CPF/CNPJ com Fernet
  - [ ] Dados bancários

### Fase 7: Testes (Semana 5-6)
- [ ] **7.1** Testes unitários:
  - [ ] `tests/unit/test_stripe_service.py`
  - [ ] `tests/unit/test_asaas_service.py`
  - [ ] `tests/unit/test_storage_service.py`

- [ ] **7.2** Testes de integração:
  - [ ] `tests/integration/test_checkout_flow.py`
  - [ ] `tests/integration/test_webhook_processing.py`

- [ ] **7.3** Testes E2E:
  - [ ] Fluxo completo Stripe (sandbox)
  - [ ] Fluxo completo Pix (sandbox Asaas)

---

## 2️⃣ CHECKLIST BANCO DE DADOS (PostgreSQL)

### Análise de Tabelas Existentes:
```sql
-- ✅ JÁ EXISTEM:
usuarios (id, email, senha_hash, tipo, ativo)
idosos (id, nome, cpf, data_nascimento)
cuidadores (id, usuario_id, idoso_id)
medicamentos (id, nome, dosagem)
agendamentos (id, idoso_id, tipo, data_hora)
alertas (id, idoso_id, tipo, mensagem)

-- ⚠️ FALTAM (para pagamentos):
subscriptions
transactions
payment_instructions
```

### Fase 1: Novas Tabelas (Semana 1)

- [ ] **1.1** Criar migration `v28_subscriptions.sql`:
  ```sql
  CREATE TABLE IF NOT EXISTS subscriptions (
      id BIGSERIAL PRIMARY KEY,
      user_id BIGINT NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
      status VARCHAR(20) DEFAULT 'trialing' CHECK (status IN ('active', 'past_due', 'canceled', 'trialing')),
      plan_tier VARCHAR(20) NOT NULL CHECK (plan_tier IN ('basic', 'gold', 'diamond')),
      current_period_start TIMESTAMP WITH TIME ZONE NOT NULL,
      current_period_end TIMESTAMP WITH TIME ZONE NOT NULL,
      payment_method_default VARCHAR(50),
      external_subscription_id VARCHAR(255) UNIQUE,
      metadata_json JSONB DEFAULT '{}',
      created_at TIMESTAMP DEFAULT NOW(),
      updated_at TIMESTAMP DEFAULT NOW()
  );
  
  CREATE INDEX idx_subscriptions_user ON subscriptions(user_id);
  CREATE INDEX idx_subscriptions_status ON subscriptions(status);
  CREATE INDEX idx_subscriptions_end_date ON subscriptions(current_period_end);
  CREATE UNIQUE INDEX idx_subscriptions_user_tier ON subscriptions(user_id, plan_tier) WHERE status = 'active';
  ```

- [ ] **1.2** Criar migration `v29_transactions.sql`:
  ```sql
  CREATE TABLE IF NOT EXISTS transactions (
      id BIGSERIAL PRIMARY KEY,
      subscription_id BIGINT REFERENCES subscriptions(id) ON DELETE SET NULL,
      user_id BIGINT NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
      amount DECIMAL(10,2) NOT NULL,
      currency VARCHAR(3) NOT NULL DEFAULT 'BRL',
      provider VARCHAR(20) NOT NULL CHECK (provider IN ('stripe', 'asaas', 'opennode', 'wise', 'nomad')),
      status VARCHAR(30) DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'failed', 'waiting_approval', 'refunded')),
      external_ref VARCHAR(255) UNIQUE,
      proof_url VARCHAR(512),
      failure_reason TEXT,
      created_at TIMESTAMP DEFAULT NOW(),
      updated_at TIMESTAMP DEFAULT NOW()
  );
  
  CREATE INDEX idx_transactions_user ON transactions(user_id);
  CREATE INDEX idx_transactions_subscription ON transactions(subscription_id);
  CREATE INDEX idx_transactions_status ON transactions(status);
  CREATE INDEX idx_transactions_external_ref ON transactions(external_ref);
  CREATE INDEX idx_transactions_created ON transactions(created_at DESC);
  ```

- [ ] **1.3** Criar migration `v30_payment_instructions.sql`:
  ```sql
  CREATE TABLE IF NOT EXISTS payment_instructions (
      id SERIAL PRIMARY KEY,
      provider VARCHAR(20) NOT NULL CHECK (provider IN ('wise', 'nomad')),
      currency VARCHAR(3) NOT NULL,
      details_json JSONB NOT NULL,
      active BOOLEAN DEFAULT TRUE,
      created_at TIMESTAMP DEFAULT NOW(),
      updated_at TIMESTAMP DEFAULT NOW()
  );
  
  CREATE INDEX idx_payment_instructions_provider ON payment_instructions(provider, currency, active);
  ```

### Fase 2: Views e Funções (Semana 1)

- [ ] **2.1** Criar view `v_active_subscriptions`:
  ```sql
  CREATE OR REPLACE VIEW v_active_subscriptions AS
  SELECT 
      s.id,
      s.user_id,
      u.email,
      i.nome as idoso_nome,
      s.plan_tier,
      s.status,
      s.current_period_start,
      s.current_period_end,
      EXTRACT(EPOCH FROM (s.current_period_end - NOW())) / 86400 as days_remaining
  FROM subscriptions s
  JOIN usuarios u ON u.id = s.user_id
  LEFT JOIN idosos i ON i.id = s.user_id
  WHERE s.status IN ('active', 'trialing')
  ORDER BY s.current_period_end ASC;
  ```

- [ ] **2.2** Criar view `v_transaction_history`:
  ```sql
  CREATE OR REPLACE VIEW v_transaction_history AS
  SELECT 
      t.id,
      t.user_id,
      u.email,
      t.amount,
      t.currency,
      t.provider,
      t.status,
      t.created_at,
      s.plan_tier
  FROM transactions t
  JOIN usuarios u ON u.id = t.user_id
  LEFT JOIN subscriptions s ON s.id = t.subscription_id
  ORDER BY t.created_at DESC;
  ```

- [ ] **2.3** Criar função `extend_subscription_period`:
  ```sql
  CREATE OR REPLACE FUNCTION extend_subscription_period(
      p_subscription_id BIGINT,
      p_days INT DEFAULT 30
  ) RETURNS VOID AS $$
  BEGIN
      UPDATE subscriptions
      SET current_period_end = current_period_end + (p_days || ' days')::INTERVAL,
          status = 'active',
          updated_at = NOW()
      WHERE id = p_subscription_id;
  END;
  $$ LANGUAGE plpgsql;
  ```

- [ ] **2.4** Criar função `check_subscription_access`:
  ```sql
  CREATE OR REPLACE FUNCTION check_subscription_access(p_user_id BIGINT)
  RETURNS BOOLEAN AS $$
  DECLARE
      has_access BOOLEAN;
  BEGIN
      SELECT EXISTS(
          SELECT 1
          FROM subscriptions
          WHERE user_id = p_user_id
            AND status = 'active'
            AND current_period_end > NOW()
      ) INTO has_access;
      
      RETURN has_access;
  END;
  $$ LANGUAGE plpgsql;
  ```

### Fase 3: Triggers (Semana 2)

- [ ] **3.1** Trigger para `updated_at` automático:
  ```sql
  CREATE OR REPLACE FUNCTION update_updated_at_column()
  RETURNS TRIGGER AS $$
  BEGIN
      NEW.updated_at = NOW();
      RETURN NEW;
  END;
  $$ LANGUAGE plpgsql;
  
  CREATE TRIGGER update_subscriptions_updated_at
      BEFORE UPDATE ON subscriptions
      FOR EACH ROW
      EXECUTE FUNCTION update_updated_at_column();
  
  CREATE TRIGGER update_transactions_updated_at
      BEFORE UPDATE ON transactions
      FOR EACH ROW
      EXECUTE FUNCTION update_updated_at_column();
  ```

- [ ] **3.2** Trigger para auditoria de mudanças de status:
  ```sql
  CREATE TABLE subscription_status_history (
      id BIGSERIAL PRIMARY KEY,
      subscription_id BIGINT REFERENCES subscriptions(id),
      old_status VARCHAR(20),
      new_status VARCHAR(20),
      changed_at TIMESTAMP DEFAULT NOW(),
      changed_by BIGINT REFERENCES usuarios(id)
  );
  
  CREATE OR REPLACE FUNCTION log_subscription_status_change()
  RETURNS TRIGGER AS $$
  BEGIN
      IF OLD.status IS DISTINCT FROM NEW.status THEN
          INSERT INTO subscription_status_history (subscription_id, old_status, new_status)
          VALUES (NEW.id, OLD.status, NEW.status);
      END IF;
      RETURN NEW;
  END;
  $$ LANGUAGE plpgsql;
  
  CREATE TRIGGER subscription_status_change_trigger
      AFTER UPDATE ON subscriptions
      FOR EACH ROW
      EXECUTE FUNCTION log_subscription_status_change();
  ```

### Fase 4: Dados Iniciais (Semana 2)

- [ ] **4.1** Popular `payment_instructions` com dados Wise:
  ```sql
  INSERT INTO payment_instructions (provider, currency, details_json, active)
  VALUES 
  ('wise', 'EUR', '{
      "account_holder": "EVA Payments Ltd",
      "iban": "DE89370400440532013000",
      "swift": "COBADEFF",
      "bank_name": "Commerzbank"
  }', true),
  ('wise', 'USD', '{
      "account_holder": "EVA Payments LLC",
      "routing_number": "026009593",
      "account_number": "1234567890",
      "bank_name": "Bank of America"
  }', true);
  ```

- [ ] **4.2** Popular `payment_instructions` com dados Nomad:
  ```sql
  INSERT INTO payment_instructions (provider, currency, details_json, active)
  VALUES 
  ('nomad', 'USD', '{
      "account_holder": "EVA Payments",
      "routing_number": "084009519",
      "account_number": "9876543210",
      "bank_name": "Nomad Global"
  }', true);
  ```

### Fase 5: Índices de Performance (Semana 2)

- [ ] **5.1** Índices compostos para queries frequentes:
  ```sql
  -- Query: Buscar transações de um usuário por período
  CREATE INDEX idx_transactions_user_created 
  ON transactions(user_id, created_at DESC);
  
  -- Query: Buscar subscriptions expirando em breve
  CREATE INDEX idx_subscriptions_status_end 
  ON subscriptions(status, current_period_end) 
  WHERE status = 'active';
  
  -- Query: Buscar transações pendentes de aprovação
  CREATE INDEX idx_transactions_status_provider 
  ON transactions(status, provider) 
  WHERE status = 'waiting_approval';
  ```

### Fase 6: Constraints e Validações (Semana 2)

- [ ] **6.1** Adicionar constraints de negócio:
  ```sql
  -- Garantir que current_period_end > current_period_start
  ALTER TABLE subscriptions
  ADD CONSTRAINT check_period_dates
  CHECK (current_period_end > current_period_start);
  
  -- Garantir que amount > 0
  ALTER TABLE transactions
  ADD CONSTRAINT check_positive_amount
  CHECK (amount > 0);
  
  -- Garantir que external_ref não seja vazio
  ALTER TABLE transactions
  ADD CONSTRAINT check_external_ref_not_empty
  CHECK (external_ref IS NULL OR length(external_ref) > 0);
  ```

---

## 3️⃣ CHECKLIST DE INTEGRAÇÃO COM PROJETOS EXISTENTES

### Integração com EVA-back (Atual)
- [ ] **3.1** Adicionar campo `subscription_tier` na tabela `usuarios`:
  ```sql
  ALTER TABLE usuarios
  ADD COLUMN subscription_tier VARCHAR(20) DEFAULT 'basic' CHECK (subscription_tier IN ('basic', 'gold', 'diamond'));
  ```

- [ ] **3.2** Criar middleware de verificação de assinatura:
  ```python
  # middleware/subscription_check.py
  async def verify_subscription_access(request: Request, call_next):
      user_id = request.state.user.id
      
      # Verificar se tem assinatura ativa
      has_access = await check_subscription_access(user_id)
      
      if not has_access and request.url.path.startswith("/api/v1/premium"):
          raise HTTPException(403, "Premium subscription required")
      
      return await call_next(request)
  ```

- [ ] **3.3** Atualizar autenticação para incluir `subscription_tier` no JWT:
  ```python
  payload = {
      "sub": str(user.id),
      "email": user.email,
      "subscription_tier": user.subscription_tier,  # ← NOVO
      "exp": expire
  }
  ```

### Integração com EVA-Front (Next.js)
- [ ] **3.4** Criar páginas:
  - [ ] `pages/pricing.tsx` - Planos e preços
  - [ ] `pages/checkout/[method].tsx` - Checkout por método
  - [ ] `pages/subscription/manage.tsx` - Gerenciar assinatura
  - [ ] `pages/admin/payments.tsx` - Admin de pagamentos

- [ ] **3.5** Criar componentes:
  - [ ] `components/PricingCard.tsx`
  - [ ] `components/PaymentMethodSelector.tsx`
  - [ ] `components/PixQRCode.tsx`
  - [ ] `components/BitcoinInvoice.tsx`
  - [ ] `components/ReceiptUploader.tsx`

### Integração com EVA-Mind (Go)
- [ ] **3.6** Adicionar verificação de subscription antes de processar:
  ```go
  // Verificar tier antes de usar features premium
  if session.SubscriptionTier == "basic" && requestedFeature == "voice_cloning" {
      return errors.New("Premium feature requires Gold or Diamond subscription")
  }
  ```

### Integração com EVA-Voice
- [ ] **3.7** Limitar clonagem de vozes por tier:
  - Basic: 0 vozes
  - Gold: 3 vozes (1 por emoção)
  - Diamond: Ilimitado

---

## 4️⃣ PRIORIZAÇÃO E CRONOGRAMA

### Sprint 1 (Semana 1-2): Fundação
1. Criar tabelas no PostgreSQL
2. Implementar schemas Pydantic
3. Configurar Stripe (sandbox)
4. Endpoint básico de checkout Stripe

### Sprint 2 (Semana 3-4): Pagamentos Automáticos
1. Implementar Asaas Pix
2. Implementar webhooks
3. Processar pagamentos automaticamente
4. Testes de integração

### Sprint 3 (Semana 5-6): Pagamentos Manuais
1. Implementar Wise/Nomad
2. Upload de comprovantes (GCS)
3. Painel admin de aprovação
4. Bitcoin Lightning (opcional)

### Sprint 4 (Semana 7-8): Frontend
1. Páginas de pricing
2. Componentes de checkout
3. Gerenciamento de assinatura
4. Testes E2E

### Sprint 5 (Semana 9-10): Produção
1. Deploy no Google Cloud
2. Monitoramento
3. Documentação
4. Treinamento da equipe

---

**Total estimado**: 10 semanas (2.5 meses)

Quer que eu comece implementando alguma parte específica?
