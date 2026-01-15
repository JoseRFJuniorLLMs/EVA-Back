# Wise Integration Checklist (v2.0 - Automated)

Baseado na especificação técnica `wise.txt`, aqui está o plano de execução passo a passo para sair do modelo manual (upload de comprovante) para o modelo automático (Wise API).

## FASE 1: Preparação & Acesso (User Action Required)
- [ ] **Criar Conta Wise Business** (Se ainda não tiver).
- [ ] **Gerar API Token** (Read-Only) em Configurações > API Tokens.
- [ ] **Obter IDs**: Profile ID e Borderless Account ID (via Curl/Postman).
- [ ] **Adicionar Variáveis de Ambiente** no `.env`:
    ```env
    WISE_API_TOKEN=...
    WISE_PROFILE_ID=...
    WISE_ACCOUNT_ID=...
    WISE_WEBHOOK_SECRET=...
    ```

## FASE 2: Banco de Dados
- [ ] **Criar Tabela `wise_payment_references`**:
    - Armazenar `reference_code` (Unique), `user_id`, `amount`, `status`, `expires_at`.
- [ ] **Atualizar `payment_instructions`**: Garantir que as instruções bancárias (IBAN, Routing) estejam corretas no DB.

## FASE 3: Backend - Core Logic
- [ ] **Implementar `WiseReferenceGenerator`**:
    - Gerar referências formato `EVA-USER-{ID}-{CRC32}`.
    - Validar Checksum.
- [ ] **Implementar `WiseAPIClient`**:
    - Wrapper para chamadas HTTP à Wise (Get Balance, Get Statement).
- [ ] **Atualizar `WebhookService`**:
    - Adicionar lógica específica para `verify_wise_signature` (HMAC-SHA256).

## FASE 4: Backend - API Routes
- [ ] **Endpoint `POST /api/checkout/wise/generate`**:
    - Gera referência única para usuário.
    - Retorna dados bancários + Referência Obrigatória.
- [ ] **Endpoint `POST /webhooks/wise`**:
    - Recebe evento `balance-deposits#credit`.
    - Busca referência no DB.
    - Ativa assinatura.
- [ ] **Endpoint `GET /api/checkout/wise/status/{ref}`**:
    - Para o frontend saber quando o pagamento caiu (Polling).

## FASE 5: Backend - Backup (Polling)
- [ ] **Celery Task**: `poll_wise_transactions` (a cada 5 min).
    - Busca últimas transações.
    - Processa caso o webhook tenha falhado.

## FASE 6: Frontend (React)
- [ ] **Atualizar `CheckoutPage - Wise Tab`**:
    - Remover input de upload de comprovante.
    - Adicionar botão "Gerar Instruções de Pagamento".
    - Exibir **Referência em Destaque** (Critical Warning).
    - Adicionar "Listening Mode" (Polling para detectar pagamento).

## FASE 7: Testes
- [ ] **Teste Unitário**: Gerador de Referência.
- [ ] **Teste de Integração**: Simular Webhook da Wise localmente.
- [ ] **Teste End-to-End**: Fluxo completo sem dinheiro real (Mock).

---
## Próximo Passo Imediato
Recomendo começar pela **Fase 2 (Database)** e **Fase 3 (Core Logic)**, pois são a base para o resto.
