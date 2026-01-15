# Hub Financeiro EVA - Especificação Técnica v3.0
## Arquitetura de Pagamentos Global com Python (FastAPI)

---

## 📋 ÍNDICE

1. [Arquitetura & Infraestrutura](#1-arquitetura--infraestrutura)
2. [Protocolos de Comunicação](#2-protocolos-de-comunicação)
3. [Especificações de APIs por Gateway](#3-especificações-de-apis-por-gateway)
4. [Schema de Banco de Dados Completo](#4-schema-de-banco-de-dados-completo)
5. [Implementação de Segurança](#5-implementação-de-segurança)
6. [Fluxos de Dados Detalhados](#6-fluxos-de-dados-detalhados)
7. [Código de Referência](#7-código-de-referência)
8. [Monitoramento & Observabilidade](#8-monitoramento--observabilidade)

---

## 1. ARQUITETURA & INFRAESTRUTURA

### 1.1 Stack Tecnológico Completo

```yaml
Backend:
  Framework: FastAPI 0.109.0
  Runtime: Python 3.11+
  ASGI Server: Uvicorn 0.27.0 (com uvloop para performance)
  
ORM & Database:
  ORM: SQLAlchemy 2.0.25 (async mode)
  Migrations: Alembic 1.13.1
  Database: PostgreSQL 16.1
  Connection Pool: asyncpg 0.29.0
  
Caching & Queue:
  Cache: Redis 7.2 (redis-py 5.0.1)
  Queue Broker: Redis (com Celery 5.3.4)
  Task Scheduler: Celery Beat 2.5.0
  
Security:
  JWT: PyJWT 2.8.0
  Password Hash: argon2-cffi 23.1.0
  Encryption: cryptography 42.0.0
  Rate Limiting: slowapi 0.1.9
  
HTTP & Integration:
  HTTP Client: httpx 0.26.0 (async support)
  Webhooks: FastAPI Webhooks
  Validation: Pydantic 2.5.3
  
Storage:
  Object Storage: Google Cloud Storage (google-cloud-storage 2.14.0)
  File Handler: aiofiles 23.2.1
  
Observability:
  Logging: structlog 24.1.0
  Metrics: prometheus-client 0.19.0
  Tracing: opentelemetry-api 1.22.0
  Error Tracking: sentry-sdk 1.40.0
  
Frontend:
  Framework: React 18.2.0 + TypeScript 5.3
  State: Redux Toolkit 2.0.1 / Zustand 4.4.7
  HTTP: Axios 1.6.5
  Forms: React Hook Form 7.49.3
  Validation: Zod 3.22.4
  UI: Material-UI 5.15.3 / Ant Design 5.12.8
  
DevOps:
  Container: Docker 25.0 + Docker Compose 2.24
  Orchestration: Kubernetes 1.29 (optional)
  Reverse Proxy: Nginx 1.25 + Let's Encrypt
  CI/CD: GitHub Actions / GitLab CI
```

### 1.2 Arquitetura de Microserviços (Modular Monolith → Microservices Ready)

```
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway (Nginx)                       │
│              ├─ Rate Limiting (1000 req/min)                │
│              ├─ SSL Termination (TLS 1.3)                   │
│              └─ Load Balancing (Round Robin)                │
└──────────────────────┬──────────────────────────────────────┘
                       │
       ┌───────────────┴───────────────┐
       │     FastAPI Application       │
       │  (Modular Router Structure)   │
       └───────────────┬───────────────┘
                       │
    ┌──────────────────┼──────────────────┐
    │                  │                  │
┌───▼────┐      ┌──────▼─────┐    ┌──────▼──────┐
│ Router │      │   Router   │    │   Router    │
│Checkout│      │ Webhooks   │    │   Admin     │
└───┬────┘      └──────┬─────┘    └──────┬──────┘
    │                  │                  │
    └──────────────────┼──────────────────┘
                       │
       ┌───────────────┴───────────────┐
       │      Service Layer            │
       │  ├─ PaymentService           │
       │  ├─ SubscriptionService      │
       │  ├─ WebhookService           │
       │  └─ NotificationService      │
       └───────────────┬───────────────┘
                       │
    ┌──────────────────┼──────────────────┐
    │                  │                  │
┌───▼────┐      ┌──────▼─────┐    ┌──────▼──────┐
│Gateway │      │   Database │    │   Storage   │
│Clients │      │ PostgreSQL │    │   GCS       │
│Stripe  │      │   + Redis  │    │             │
│Asaas   │      │            │    │             │
│OpenNode│      │            │    │             │
└────────┘      └────────────┘    └─────────────┘
```

### 1.3 Estrutura de Diretórios Python

```
api_financeiro/
├── alembic/                      # Database migrations
│   ├── versions/
│   └── env.py
├── app/
│   ├── __init__.py
│   ├── main.py                   # FastAPI application entry
│   ├── config.py                 # Settings with pydantic-settings
│   ├── dependencies.py           # Dependency injection (DB session, auth)
│   │
│   ├── api/                      # API Layer (Routers)
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── checkout.py       # POST /checkout/*
│   │   │   ├── webhooks.py       # POST /webhooks/*
│   │   │   ├── admin.py          # GET/POST /admin/*
│   │   │   └── transactions.py   # GET /transactions/*
│   │   └── deps.py               # Router-specific dependencies
│   │
│   ├── core/                     # Core Infrastructure
│   │   ├── __init__.py
│   │   ├── security.py           # JWT, password hashing, encryption
│   │   ├── config.py             # Configuration schemas
│   │   ├── database.py           # Database engine & session
│   │   ├── redis.py              # Redis connection pool
│   │   └── celery_app.py         # Celery configuration
│   │
│   ├── models/                   # SQLAlchemy ORM Models
│   │   ├── __init__.py
│   │   ├── base.py               # Base model with common fields
│   │   ├── user.py
│   │   ├── subscription.py
│   │   ├── transaction.py
│   │   └── payment_instruction.py
│   │
│   ├── schemas/                  # Pydantic Schemas (Request/Response)
│   │   ├── __init__.py
│   │   ├── checkout.py
│   │   ├── webhook.py
│   │   ├── transaction.py
│   │   └── subscription.py
│   │
│   ├── services/                 # Business Logic Layer
│   │   ├── __init__.py
│   │   ├── payment/
│   │   │   ├── __init__.py
│   │   │   ├── base.py           # Abstract base payment provider
│   │   │   ├── stripe.py         # Stripe integration
│   │   │   ├── asaas.py          # Asaas Pix integration
│   │   │   ├── opennode.py       # Bitcoin Lightning integration
│   │   │   └── factory.py        # Payment provider factory
│   │   ├── subscription.py       # Subscription lifecycle management
│   │   ├── webhook_handler.py    # Webhook processing & validation
│   │   ├── notification.py       # Email/SMS/Push notifications
│   │   └── storage.py            # S3 file upload/download
│   │
│   ├── tasks/                    # Celery Tasks
│   │   ├── __init__.py
│   │   ├── payment.py            # Async payment processing
│   │   ├── subscription.py       # Subscription renewal reminders
│   │   └── reporting.py          # Daily/monthly reports
│   │
│   ├── middleware/               # Custom Middleware
│   │   ├── __init__.py
│   │   ├── rate_limit.py
│   │   ├── logging.py
│   │   └── error_handler.py
│   │
│   └── utils/                    # Utilities
│       ├── __init__.py
│       ├── currency.py           # Currency conversion
│       ├── validators.py         # Custom validators
│       └── helpers.py            # General helpers
│
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── conftest.py               # Pytest fixtures
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── scripts/                      # Utility scripts
│   ├── seed_db.py
│   └── migrate_data.py
│
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── .env.example
├── .env
├── requirements.txt
├── pyproject.toml                # Poetry dependencies
└── README.md
```

---

## 2. PROTOCOLOS DE COMUNICAÇÃO

### 2.1 HTTP/REST API Standards

**Protocolo Base:**
- HTTP/2 over TLS 1.3 (obrigatório)
- Content-Type: `application/json; charset=utf-8`
- Encoding: UTF-8
- Compression: gzip (Accept-Encoding)

**Status Codes:**
```
200 OK              - Request successful
201 Created         - Resource created (e.g., transaction)
202 Accepted        - Async processing started (webhooks)
400 Bad Request     - Invalid input (validation error)
401 Unauthorized    - Missing/invalid token
403 Forbidden       - Insufficient permissions
404 Not Found       - Resource doesn't exist
409 Conflict        - Duplicate transaction (idempotency)
422 Unprocessable   - Business logic error
429 Too Many Req    - Rate limit exceeded
500 Internal Error  - Server error
503 Service Unavail - Gateway timeout
```

**Headers Obrigatórios:**
```http
# Request
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
X-Request-ID: <uuid4>           # Para tracing
X-Idempotency-Key: <uuid4>      # Para operações de criação
User-Agent: EVA-Web/1.0

# Response
X-Request-ID: <uuid4>           # Echo do request
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1705320000   # Unix timestamp
```

### 2.2 WebSocket para Atualizações em Tempo Real

**Protocolo:** WebSocket Secure (wss://)

```python
# FastAPI WebSocket endpoint
from fastapi import WebSocket

@app.websocket("/ws/payment/{transaction_id}")
async def payment_status_websocket(
    websocket: WebSocket,
    transaction_id: int,
    token: str = Query(...)
):
    await websocket.accept()
    
    # Validate JWT
    user = await verify_token(token)
    
    # Subscribe to Redis pub/sub
    pubsub = redis.pubsub()
    await pubsub.subscribe(f"payment:{transaction_id}")
    
    try:
        async for message in pubsub.listen():
            if message['type'] == 'message':
                await websocket.send_json({
                    "event": "payment_update",
                    "data": json.loads(message['data']),
                    "timestamp": datetime.utcnow().isoformat()
                })
    except WebSocketDisconnect:
        await pubsub.unsubscribe(f"payment:{transaction_id}")
```

**Mensagens do Cliente → Servidor:**
```json
{
  "action": "subscribe",
  "transaction_id": 12345,
  "timestamp": "2026-01-15T10:30:00Z"
}
```

**Mensagens do Servidor → Cliente:**
```json
{
  "event": "payment_confirmed",
  "data": {
    "transaction_id": 12345,
    "status": "paid",
    "amount": 59.90,
    "currency": "BRL"
  },
  "timestamp": "2026-01-15T10:32:15Z"
}
```

### 2.3 Webhook Protocol (Entrada de Gateways)

**Especificação:**
- Method: `POST`
- Content-Type: `application/json`
- Retry: Exponential backoff (5s, 25s, 125s, 625s)
- Timeout: 30 segundos
- Idempotency: Baseado em `external_ref`

**Validação de Assinatura (HMAC-SHA256):**

```python
import hmac
import hashlib

def verify_webhook_signature(
    payload: bytes,
    signature: str,
    secret: str,
    algorithm: str = "sha256"
) -> bool:
    """
    Valida webhook usando HMAC.
    
    Args:
        payload: Raw body da request (bytes)
        signature: Header X-Signature ou Stripe-Signature
        secret: Webhook secret do gateway
        algorithm: sha256 ou sha512
    """
    expected = hmac.new(
        key=secret.encode(),
        msg=payload,
        digestmod=getattr(hashlib, algorithm)
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature)
```

**Request Handling:**
```python
from fastapi import Request, HTTPException

@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")
    
    try:
        # Stripe SDK validation
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(400, "Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(400, "Invalid signature")
    
    # Process async
    await process_webhook_task.delay(event.to_dict())
    
    return {"received": True}
```

---

## 3. ESPECIFICAÇÕES DE APIS POR GATEWAY

### 3.1 Stripe API (Cartão de Crédito)

**SDK:** `stripe==10.12.0`

**Configuração:**
```python
import stripe
from app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = "2024-11-20.acacia"  # Versão fixa
```

**A. Criação de Checkout Session:**

```python
from stripe import checkout

async def create_stripe_session(
    plan_tier: str,
    frequency: str,  # monthly | yearly
    user_id: int,
    success_url: str,
    cancel_url: str
) -> dict:
    """
    Cria sessão de checkout do Stripe.
    
    Returns:
        {
            "url": "https://checkout.stripe.com/c/pay/...",
            "session_id": "cs_test_...",
            "expires_at": 1705320000
        }
    """
    # Map plan to price ID (configurado no Stripe Dashboard)
    price_map = {
        ("gold", "monthly"): "price_1OXxxx",
        ("gold", "yearly"): "price_1OYxxx",
        ("diamond", "monthly"): "price_1OZxxx",
        ("diamond", "yearly"): "price_1PAxxx",
    }
    
    price_id = price_map.get((plan_tier, frequency))
    if not price_id:
        raise ValueError(f"Invalid plan: {plan_tier}/{frequency}")
    
    session = checkout.Session.create(
        mode="subscription",
        line_items=[{
            "price": price_id,
            "quantity": 1,
        }],
        success_url=f"{success_url}?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=cancel_url,
        client_reference_id=str(user_id),  # Para vincular ao user
        metadata={
            "user_id": str(user_id),
            "plan_tier": plan_tier,
            "frequency": frequency
        },
        subscription_data={
            "metadata": {
                "user_id": str(user_id),
                "plan_tier": plan_tier
            }
        },
        expires_at=int((datetime.utcnow() + timedelta(hours=1)).timestamp()),
        automatic_tax={"enabled": True},  # Se aplicável
        billing_address_collection="required"
    )
    
    return {
        "url": session.url,
        "session_id": session.id,
        "expires_at": session.expires_at
    }
```

**B. Webhook Events (Principais):**

| Event | Descrição | Ação |
|-------|-----------|------|
| `checkout.session.completed` | Pagamento inicial bem-sucedido | Ativar subscription |
| `invoice.paid` | Cobrança recorrente paga | Renovar período |
| `invoice.payment_failed` | Falha no pagamento | Atualizar status para past_due |
| `customer.subscription.deleted` | Assinatura cancelada | Marcar como canceled |
| `customer.subscription.updated` | Alteração de plano | Atualizar tier |

**Webhook Handler:**
```python
async def handle_stripe_webhook(event: dict) -> None:
    event_type = event["type"]
    
    if event_type == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = int(session["metadata"]["user_id"])
        
        # Criar subscription no DB
        subscription = await create_subscription(
            user_id=user_id,
            plan_tier=session["metadata"]["plan_tier"],
            payment_method="stripe_card",
            external_subscription_id=session["subscription"],
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=30)
        )
        
        # Criar transaction
        await create_transaction(
            subscription_id=subscription.id,
            user_id=user_id,
            amount=session["amount_total"] / 100,  # Cents → BRL
            currency="BRL",
            provider="stripe",
            status="paid",
            external_ref=session["id"]
        )
    
    elif event_type == "invoice.payment_failed":
        invoice = event["data"]["object"]
        subscription_id = invoice["subscription"]
        
        # Atualizar status
        await update_subscription_status(
            external_subscription_id=subscription_id,
            status="past_due"
        )
        
        # Enviar notificação
        await send_payment_failed_notification(subscription_id)
```

### 3.2 Asaas API (Pix)

**SDK:** Não oficial, usar `httpx`

**Base URL:** `https://api.asaas.com/v3`

**Autenticação:**
```python
headers = {
    "Authorization": f"Bearer {settings.ASAAS_API_KEY}",
    "Content-Type": "application/json"
}
```

**A. Criar Cobrança Pix:**

```python
import httpx
from decimal import Decimal

async def create_asaas_pix_charge(
    user_id: int,
    amount: Decimal,
    plan_tier: str
) -> dict:
    """
    Cria cobrança Pix no Asaas.
    
    Returns:
        {
            "charge_id": "pay_xxx",
            "qr_code_url": "https://asaas.com/qr/xxx.png",
            "qr_code_payload": "00020126...",
            "expires_at": "2026-01-15T12:00:00Z"
        }
    """
    async with httpx.AsyncClient() as client:
        # 1. Criar/buscar customer
        customer_response = await client.post(
            "https://api.asaas.com/v3/customers",
            headers=headers,
            json={
                "name": f"User {user_id}",
                "cpfCnpj": "00000000000",  # Fake para dev
                "externalReference": str(user_id)
            }
        )
        customer = customer_response.json()
        
        # 2. Criar cobrança
        charge_response = await client.post(
            "https://api.asaas.com/v3/payments",
            headers=headers,
            json={
                "customer": customer["id"],
                "billingType": "PIX",
                "value": float(amount),
                "dueDate": (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d"),
                "description": f"EVA {plan_tier.title()} - Assinatura",
                "externalReference": f"user_{user_id}_{datetime.utcnow().timestamp()}",
                "postalService": False
            }
        )
        charge = charge_response.json()
        
        # 3. Obter QR Code
        qr_response = await client.get(
            f"https://api.asaas.com/v3/payments/{charge['id']}/pixQrCode",
            headers=headers
        )
        qr_data = qr_response.json()
        
        return {
            "charge_id": charge["id"],
            "qr_code_url": qr_data.get("encodedImage"),  # Base64 ou URL
            "qr_code_payload": qr_data["payload"],  # Copia e cola
            "expires_at": qr_data["expirationDate"]
        }
```

**B. Webhook Events:**

| Event | Descrição | Campo `event` |
|-------|-----------|---------------|
| Pagamento Confirmado | Pix recebido | `PAYMENT_RECEIVED` |
| Pagamento Vencido | Não pago no prazo | `PAYMENT_OVERDUE` |
| Estorno | Devolução de pagamento | `PAYMENT_REFUNDED` |

**Webhook Validation (Asaas usa Token fixo):**
```python
@app.post("/webhooks/asaas")
async def asaas_webhook(request: Request):
    # Asaas envia token em query param ou header
    token = request.query_params.get("token") or request.headers.get("asaas-access-token")
    
    if token != settings.ASAAS_WEBHOOK_TOKEN:
        raise HTTPException(401, "Invalid token")
    
    payload = await request.json()
    event_type = payload.get("event")
    
    if event_type == "PAYMENT_RECEIVED":
        payment = payload["payment"]
        external_ref = payment["externalReference"]
        
        # Atualizar transaction
        await update_transaction_by_external_ref(
            external_ref=external_ref,
            status="paid"
        )
        
        # Ativar subscription
        await activate_subscription_from_transaction(external_ref)
    
    return {"received": True}
```

### 3.3 OpenNode API (Bitcoin Lightning)

**SDK:** `opennode==0.4.0` ou API REST

**Base URL:** `https://api.opennode.com/v1`

**Autenticação:**
```http
Authorization: <API_KEY>
```

**A. Criar Invoice Lightning:**

```python
import httpx
from decimal import Decimal

async def create_lightning_invoice(
    user_id: int,
    amount_brl: Decimal,
    plan_tier: str
) -> dict:
    """
    Cria invoice Lightning Network via OpenNode.
    
    Converte BRL → BTC usando Coingecko API.
    
    Returns:
        {
            "invoice_id": "abc123",
            "lightning_invoice": "lnbc15u1p...",
            "qr_code_url": "https://chart.googleapis.com/chart?chs=300x300&cht=qr&chl=lnbc...",
            "amount_btc": 0.00015000,
            "amount_brl": 59.90,
            "expires_at": "2026-01-15T10:45:00Z"
        }
    """
    # 1. Obter cotação BTC/BRL
    async with httpx.AsyncClient() as client:
        cg_response = await client.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "bitcoin", "vs_currencies": "brl"}
        )
        btc_price_brl = Decimal(str(cg_response.json()["bitcoin"]["brl"]))
        
        # Adicionar 5% buffer para volatilidade
        amount_btc = (amount_brl / btc_price_brl) * Decimal("1.05")
        amount_satoshis = int(amount_btc * 100_000_000)
        
        # 2. Criar invoice no OpenNode
        on_response = await client.post(
            "https://api.opennode.com/v1/charges",
            headers={"Authorization": settings.OPENNODE_API_KEY},
            json={
                "amount": amount_satoshis,
                "currency": "btc",
                "description": f"EVA {plan_tier.title()} Subscription",
                "callback_url": f"{settings.API_BASE_URL}/webhooks/opennode",
                "success_url": f"{settings.FRONTEND_URL}/payment/success",
                "customer_email": f"user{user_id}@eva.com",
                "order_id": f"user_{user_id}_{int(datetime.utcnow().timestamp())}",
                "ttl": 900  # 15 minutos
            }
        )
        invoice = on_response.json()["data"]
        
        return {
            "invoice_id": invoice["id"],
            "lightning_invoice": invoice["lightning_invoice"]["payreq"],
            "qr_code_url": f"https://chart.googleapis.com/chart?chs=300x300&cht=qr&chl={invoice['lightning_invoice']['payreq']}",
            "amount_btc": float(amount_btc),
            "amount_brl": float(amount_brl),
            "expires_at": invoice["expires_at"]
        }
```

**B. Webhook Events:**

| Status | Descrição |
|--------|-----------|
| `paid` | Invoice pago com sucesso |
| `expired` | Invoice expirou (15 min) |
| `processing` | Confirmação em andamento |

**Webhook Handler:**
```python
@app.post("/webhooks/opennode")
async def opennode_webhook(request: Request):
    payload = await request.json()
    
    # OpenNode envia HMAC no header
    signature = request.headers.get("opennode-signature")
    is_valid = verify_webhook_signature(
        payload=await request.body(),
        signature=signature,
        secret=settings.OPENNODE_WEBHOOK_SECRET
    )
    
    if not is_valid:
        raise HTTPException(401, "Invalid signature")
    
    if payload["status"] == "paid":
        order_id = payload["order_id"]
        
        # Atualizar transaction
        await update_transaction_by_external_ref(
            external_ref=order_id,
            status="paid"
        )
        
        # Ativar subscription
        await activate_subscription_from_transaction(order_id)
    
    return {"received": True}
```

### 3.4 Wise API (Transferência Internacional)

**SDK:** Não oficial, usar `httpx`

**Base URL:** `https://api.wise.com/v3`

**Autenticação:** Bearer Token (OAuth 2.0 ou API Key)

**A. Obter Instruções Bancárias:**

```python
async def get_wise_instructions(
    currency: str = "EUR"
) -> dict:
    """
    Retorna instruções de transferência para conta Wise.
    
    Nota: Dados estáticos, armazenados no DB (tabela payment_instructions).
    """
    instructions = await db.query(PaymentInstruction).filter(
        PaymentInstruction.provider == "wise",
        PaymentInstruction.currency == currency,
        PaymentInstruction.active == True
    ).first()
    
    if not instructions:
        raise ValueError(f"No instructions for Wise/{currency}")
    
    return {
        "provider": "wise",
        "currency": currency,
        "details": instructions.details_json,
        # Exemplo details_json:
        # {
        #   "account_holder": "EVA Payments Ltd",
        #   "iban": "DE89370400440532013000",
        #   "swift": "COBADEFF",
        #   "reference": "EVA-USER-12345"  # Gerado dinamicamente
        # }
    }
```

**B. Verificação Manual:**

- Usuário envia comprovante (PDF/imagem)
- Admin verifica no painel Wise
- Confirma transação no sistema EVA

**Upload de Comprovante:**

```python
from fastapi import UploadFile
from google.cloud import storage
from uuid import uuid4

async def upload_payment_receipt(
    file: UploadFile,
    transaction_id: int,
    user_id: int
) -> str:
    """
    Faz upload de comprovante para Google Cloud Storage e retorna URL.
    
    Returns:
        "https://storage.googleapis.com/eva-receipts/receipts/xxx.pdf"
    """
    # Validação
    if file.content_type not in ["image/jpeg", "image/png", "application/pdf"]:
        raise ValueError("Invalid file type")
    
    if file.size > 5 * 1024 * 1024:  # 5MB
        raise ValueError("File too large")
    
    # Upload para GCS
    storage_client = storage.Client(
        project=settings.GCP_PROJECT_ID
    )
    bucket = storage_client.bucket(settings.GCS_BUCKET_NAME)
    
    file_ext = file.filename.split(".")[-1]
    blob_name = f"receipts/{user_id}/{transaction_id}_{uuid4().hex}.{file_ext}"
    blob = bucket.blob(blob_name)
    
    # Upload com metadata
    blob.upload_from_file(
        file.file,
        content_type=file.content_type
    )
    
    # Atualizar transaction
    proof_url = f"https://storage.googleapis.com/{settings.GCS_BUCKET_NAME}/{blob_name}"
    await update_transaction(
        transaction_id=transaction_id,
        proof_url=proof_url,
        status="waiting_approval"
    )
    
    # Notificar admin
    await send_admin_notification(
        subject=f"New receipt for Transaction #{transaction_id}",
        body=f"User {user_id} uploaded receipt: {proof_url}"
    )
    
    return proof_url
```

### 3.5 Nomad API (Conta Global)

**Similar ao Wise, com instruções estáticas.**

**Diferenças:**
- Suporta USD, EUR, GBP
- Transferências via ACH (EUA) ou SWIFT
- Verificação manual obrigatória

### 3.6 Google Cloud Storage (Armazenamento de Comprovantes)

**SDK:** `google-cloud-storage==2.14.0`

**Autenticação:**
```python
from google.cloud import storage
from google.oauth2 import service_account

# Método 1: Usar variável de ambiente GOOGLE_APPLICATION_CREDENTIALS
# export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
storage_client = storage.Client()

# Método 2: Explícito via código
credentials = service_account.Credentials.from_service_account_file(
    settings.GCS_CREDENTIALS_PATH
)
storage_client = storage.Client(
    project=settings.GCP_PROJECT_ID,
    credentials=credentials
)
```

**A. Upload de Arquivo (Síncrono):**

```python
from google.cloud import storage
from uuid import uuid4

def upload_to_gcs(
    file_content: bytes,
    file_name: str,
    content_type: str,
    bucket_name: str,
    folder: str = "receipts"
) -> str:
    """
    Upload de arquivo para GCS.
    
    Args:
        file_content: Conteúdo do arquivo em bytes
        file_name: Nome do arquivo
        content_type: MIME type (image/jpeg, application/pdf, etc)
        bucket_name: Nome do bucket GCS
        folder: Pasta dentro do bucket
    
    Returns:
        URL pública do arquivo
    """
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    
    # Gerar nome único
    blob_name = f"{folder}/{uuid4().hex}_{file_name}"
    blob = bucket.blob(blob_name)
    
    # Upload com metadata
    blob.upload_from_string(
        file_content,
        content_type=content_type
    )
    
    # Definir metadata customizado
    blob.metadata = {
        "uploaded_at": datetime.utcnow().isoformat(),
        "original_name": file_name
    }
    blob.patch()
    
    # Tornar público (opcional)
    # blob.make_public()
    
    # Retornar URL
    return f"https://storage.googleapis.com/{bucket_name}/{blob_name}"
```

**B. Upload Assíncrono (FastAPI):**

```python
from fastapi import UploadFile
from google.cloud import storage
import aiofiles

async def upload_receipt_async(
    file: UploadFile,
    user_id: int,
    transaction_id: int
) -> dict:
    """
    Upload assíncrono de comprovante para GCS.
    
    Returns:
        {
            "url": "https://storage.googleapis.com/...",
            "blob_name": "receipts/xxx.pdf",
            "size": 123456
        }
    """
    # Ler conteúdo
    content = await file.read()
    
    # Validar tamanho
    if len(content) > 5 * 1024 * 1024:  # 5MB
        raise ValueError("File too large (max 5MB)")
    
    # Validar tipo
    allowed_types = ["image/jpeg", "image/png", "application/pdf"]
    if file.content_type not in allowed_types:
        raise ValueError(f"Invalid type. Allowed: {allowed_types}")
    
    # Upload para GCS (operação síncrona dentro de executor)
    client = storage.Client()
    bucket = client.bucket(settings.GCS_BUCKET_NAME)
    
    file_ext = file.filename.split(".")[-1]
    blob_name = f"receipts/{user_id}/{transaction_id}_{uuid4().hex}.{file_ext}"
    blob = bucket.blob(blob_name)
    
    # Upload
    blob.upload_from_string(
        content,
        content_type=file.content_type
    )
    
    # Metadata
    blob.metadata = {
        "user_id": str(user_id),
        "transaction_id": str(transaction_id),
        "uploaded_at": datetime.utcnow().isoformat()
    }
    blob.patch()
    
    return {
        "url": f"https://storage.googleapis.com/{settings.GCS_BUCKET_NAME}/{blob_name}",
        "blob_name": blob_name,
        "size": blob.size
    }
```

**C. Gerar Signed URL (Acesso Temporário):**

```python
from datetime import timedelta

def generate_signed_url(
    blob_name: str,
    bucket_name: str,
    expiration_minutes: int = 60
) -> str:
    """
    Gera URL assinada com expiração.
    
    Útil para downloads privados sem tornar arquivo público.
    
    Args:
        blob_name: Nome do blob no GCS (e.g., "receipts/xxx.pdf")
        bucket_name: Nome do bucket
        expiration_minutes: Tempo de expiração em minutos
    
    Returns:
        URL assinada com token de acesso temporário
    """
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=expiration_minutes),
        method="GET"
    )
    
    return url
```

**D. Download de Arquivo:**

```python
async def download_from_gcs(blob_name: str) -> bytes:
    """
    Download de arquivo do GCS.
    
    Args:
        blob_name: Nome do blob (e.g., "receipts/user_123/xxx.pdf")
    
    Returns:
        Conteúdo do arquivo em bytes
    """
    client = storage.Client()
    bucket = client.bucket(settings.GCS_BUCKET_NAME)
    blob = bucket.blob(blob_name)
    
    if not blob.exists():
        raise FileNotFoundError(f"Blob {blob_name} not found")
    
    # Download para memória
    content = blob.download_as_bytes()
    
    return content
```

**E. Listar Arquivos (com paginação):**

```python
def list_user_receipts(
    user_id: int,
    page_size: int = 50,
    page_token: str = None
) -> dict:
    """
    Lista comprovantes de um usuário.
    
    Returns:
        {
            "files": [
                {
                    "name": "receipts/123/xxx.pdf",
                    "size": 123456,
                    "created": "2026-01-15T10:30:00Z",
                    "url": "https://storage.googleapis.com/..."
                }
            ],
            "next_page_token": "token_for_next_page"
        }
    """
    client = storage.Client()
    bucket = client.bucket(settings.GCS_BUCKET_NAME)
    
    prefix = f"receipts/{user_id}/"
    
    blobs = bucket.list_blobs(
        prefix=prefix,
        max_results=page_size,
        page_token=page_token
    )
    
    files = []
    for blob in blobs:
        files.append({
            "name": blob.name,
            "size": blob.size,
            "created": blob.time_created.isoformat(),
            "url": f"https://storage.googleapis.com/{settings.GCS_BUCKET_NAME}/{blob.name}",
            "metadata": blob.metadata or {}
        })
    
    return {
        "files": files,
        "next_page_token": blobs.next_page_token
    }
```

**F. Deletar Arquivo:**

```python
def delete_from_gcs(blob_name: str) -> bool:
    """
    Remove arquivo do GCS.
    
    Args:
        blob_name: Nome do blob
    
    Returns:
        True se deletado com sucesso
    """
    client = storage.Client()
    bucket = client.bucket(settings.GCS_BUCKET_NAME)
    blob = bucket.blob(blob_name)
    
    if not blob.exists():
        return False
    
    blob.delete()
    return True
```

**G. Configuração de CORS (para uploads diretos do frontend):**

```python
def configure_bucket_cors():
    """
    Configura CORS no bucket para uploads diretos.
    
    Permite que o frontend faça upload direto para GCS
    sem passar pelo backend (reduz carga no servidor).
    """
    client = storage.Client()
    bucket = client.bucket(settings.GCS_BUCKET_NAME)
    
    bucket.cors = [
        {
            "origin": ["https://app.eva.com"],
            "method": ["GET", "POST", "PUT"],
            "responseHeader": ["Content-Type"],
            "maxAgeSeconds": 3600
        }
    ]
    bucket.patch()
```

**H. Lifecycle Policy (Limpeza Automática):**

```python
def setup_lifecycle_policy():
    """
    Configura política de lifecycle para deletar arquivos antigos.
    
    Exemplo: Deletar comprovantes após 7 anos (compliance GDPR).
    """
    from google.cloud.storage import Bucket
    
    client = storage.Client()
    bucket = client.bucket(settings.GCS_BUCKET_NAME)
    
    rule = {
        "action": {"type": "Delete"},
        "condition": {
            "age": 2555,  # 7 anos em dias
            "matchesPrefix": ["receipts/"]
        }
    }
    
    bucket.lifecycle_rules = [rule]
    bucket.patch()
```

**I. Endpoint Completo: Upload de Comprovante:**

```python
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.services.storage import upload_receipt_async
from app.models.transaction import Transaction
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/receipts", tags=["Receipts"])

@router.post("/upload/{transaction_id}")
async def upload_receipt(
    transaction_id: int,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload de comprovante de pagamento.
    
    **Validações:**
    - Tamanho máximo: 5MB
    - Tipos aceitos: JPEG, PNG, PDF
    - Transação deve pertencer ao usuário
    
    **Returns:**
    - URL do arquivo no GCS
    - Status atualizado para waiting_approval
    """
    # Verificar ownership da transaction
    transaction = await db.get(Transaction, transaction_id)
    
    if not transaction:
        raise HTTPException(404, "Transaction not found")
    
    if transaction.user_id != user.id:
        raise HTTPException(403, "Not authorized")
    
    if transaction.status != "pending":
        raise HTTPException(400, "Transaction already processed")
    
    try:
        # Upload para GCS
        result = await upload_receipt_async(
            file=file,
            user_id=user.id,
            transaction_id=transaction_id
        )
        
        # Atualizar transaction
        transaction.proof_url = result["url"]
        transaction.status = "waiting_approval"
        await db.commit()
        
        # Notificar admin
        await send_admin_notification(
            subject=f"New receipt uploaded - Transaction #{transaction_id}",
            body=f"User {user.email} uploaded receipt. Review at: {result['url']}"
        )
        
        return {
            "message": "Receipt uploaded successfully",
            "url": result["url"],
            "transaction_id": transaction_id,
            "status": "waiting_approval"
        }
    
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error(f"Upload error: {e}", extra={"user_id": user.id})
        raise HTTPException(500, "Upload failed")
```

**J. Melhores Práticas GCS:**

1. **Usar Service Account** com permissões mínimas:
   ```json
   {
     "roles": [
       "roles/storage.objectCreator",
       "roles/storage.objectViewer"
     ]
   }
   ```

2. **Habilitar versionamento** para auditoria:
   ```python
   bucket.versioning_enabled = True
   bucket.patch()
   ```

3. **Encriptação at rest** (padrão: Google-managed keys):
   ```python
   # Ou usar Customer-Managed Encryption Keys (CMEK)
   blob.customer_encryption = {
       "encryption_algorithm": "AES256",
       "key_sha256": "..."
   }
   ```

4. **Monitoramento** via Cloud Logging:
   ```python
   from google.cloud import logging_v2
   
   logging_client = logging_v2.Client()
   logger = logging_client.logger("gcs-uploads")
   
   logger.log_struct({
       "event": "file_uploaded",
       "user_id": user_id,
       "blob_name": blob_name,
       "size": blob.size
   })
   ```

5. **Custo otimizado** com Storage Classes:
   - **Standard**: Acesso frequente (receipts recentes)
   - **Nearline**: Acesso mensal (receipts antigos)
   - **Coldline**: Acesso anual (arquivamento)
   - **Archive**: Compliance (7+ anos)

---

## 4. SCHEMA DE BANCO DE DADOS COMPLETO

### 4.1 Modelagem PostgreSQL (SQLAlchemy 2.0)

**Base Model:**

```python
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TimestampMixin:
    """Mixin para timestamps automáticos."""
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
```

**Tabela: users**

```python
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    
    __table_args__ = (
        Index("idx_users_email_active", "email", "is_active"),
    )
```

**Tabela: subscriptions**

```python
from sqlalchemy import (
    Column, Integer, String, Enum, DateTime, ForeignKey, JSON, Index
)
import enum

class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    TRIALING = "trialing"

class PlanTier(str, enum.Enum):
    BASIC = "basic"
    GOLD = "gold"
    DIAMOND = "diamond"

class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.TRIALING)
    plan_tier = Column(Enum(PlanTier), nullable=False)
    
    current_period_start = Column(DateTime(timezone=True), nullable=False)
    current_period_end = Column(DateTime(timezone=True), nullable=False, index=True)
    
    payment_method_default = Column(String(50))  # stripe_card, asaas_pix, etc.
    external_subscription_id = Column(String(255), unique=True, nullable=True)
    
    metadata_json = Column(JSON, default={})  # {frequency: monthly, ...}
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    transactions = relationship("Transaction", back_populates="subscription")
    
    __table_args__ = (
        Index("idx_sub_user_tier", "user_id", "plan_tier", unique=True),
        Index("idx_sub_status_end", "status", "current_period_end"),
    )
```

**Tabela: transactions**

```python
from decimal import Decimal

class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    WAITING_APPROVAL = "waiting_approval"
    REFUNDED = "refunded"

class PaymentProvider(str, enum.Enum):
    STRIPE = "stripe"
    ASAAS = "asaas"
    OPENNODE = "opennode"
    WISE = "wise"
    NOMAD = "nomad"

class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False)  # BRL, USD, BTC
    
    provider = Column(Enum(PaymentProvider), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    
    external_ref = Column(String(255), unique=True, nullable=True, index=True)
    proof_url = Column(String(512), nullable=True)
    failure_reason = Column(Text, nullable=True)
    
    # Relationships
    subscription = relationship("Subscription", back_populates="transactions")
    user = relationship("User", back_populates="transactions")
    
    __table_args__ = (
        Index("idx_trans_user_created", "user_id", "created_at", postgresql_using="btree"),
        Index("idx_trans_status_provider", "status", "provider"),
    )
```

**Tabela: payment_instructions**

```python
class PaymentInstruction(Base, TimestampMixin):
    __tablename__ = "payment_instructions"
    
    id = Column(Integer, primary_key=True)
    provider = Column(Enum(PaymentProvider), nullable=False)
    currency = Column(String(3), nullable=False)
    
    details_json = Column(JSON, nullable=False)
    # Exemplo:
    # {
    #   "account_holder": "EVA Payments",
    #   "iban": "DE89...",
    #   "swift": "COBADEFF",
    #   "routing_number": "026009593"  # Para ACH
    # }
    
    active = Column(Boolean, default=True)
    
    __table_args__ = (
        Index("idx_instructions_provider_currency", "provider", "currency", "active"),
    )
```

### 4.2 Migrations com Alembic

**Criar migration inicial:**

```bash
# Init Alembic
alembic init alembic

# Editar alembic.ini
# sqlalchemy.url = postgresql+asyncpg://user:pass@localhost/eva_db

# Criar primeira migration
alembic revision --autogenerate -m "Initial schema"

# Aplicar
alembic upgrade head
```

**Migration exemplo (adicionar campo):**

```python
# alembic/versions/xxx_add_refund_reason.py

def upgrade():
    op.add_column(
        'transactions',
        sa.Column('refund_reason', sa.Text(), nullable=True)
    )

def downgrade():
    op.drop_column('transactions', 'refund_reason')
```

---

## 5. IMPLEMENTAÇÃO DE SEGURANÇA

### 5.1 Autenticação JWT

**Esquema:**
- Algorithm: RS256 (assymetric)
- Token Lifetime: 15 minutos (access) + 7 dias (refresh)
- Storage: Redis (para blacklist)

**Geração de Token:**

```python
from datetime import datetime, timedelta
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Carregar chaves RSA
with open("keys/private.pem", "rb") as f:
    PRIVATE_KEY = serialization.load_pem_private_key(
        f.read(),
        password=None,
        backend=default_backend()
    )

with open("keys/public.pem", "rb") as f:
    PUBLIC_KEY = serialization.load_pem_public_key(
        f.read(),
        backend=default_backend()
    )

def create_access_token(user_id: int, is_admin: bool = False) -> str:
    """Cria JWT com claims customizados."""
    expire = datetime.utcnow() + timedelta(minutes=15)
    
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access",
        "is_admin": is_admin
    }
    
    return jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")

def create_refresh_token(user_id: int) -> str:
    """Token de refresh (7 dias)."""
    expire = datetime.utcnow() + timedelta(days=7)
    
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    }
    
    return jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")

def verify_token(token: str) -> dict:
    """Valida e decodifica JWT."""
    try:
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
        
        # Verificar blacklist
        if await redis.exists(f"blacklist:{token}"):
            raise jwt.InvalidTokenError("Token blacklisted")
        
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")
```

**Dependency Injection:**

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Extrai user do JWT."""
    token = credentials.credentials
    payload = verify_token(token)
    
    user_id = int(payload["sub"])
    user = await db.get(User, user_id)
    
    if not user or not user.is_active:
        raise HTTPException(401, "Invalid user")
    
    return user

async def require_admin(user: User = Depends(get_current_user)) -> User:
    """Requer permissões de admin."""
    if not user.is_admin:
        raise HTTPException(403, "Admin required")
    return user
```

### 5.2 Criptografia de Dados Sensíveis

**Senhas (Argon2id):**

```python
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher(
    time_cost=2,       # Iterations
    memory_cost=65536, # 64 MB
    parallelism=4,     # Threads
    hash_len=32,       # Output length
    salt_len=16
)

def hash_password(password: str) -> str:
    """Hash com Argon2id."""
    return ph.hash(password)

def verify_password(password: str, hash: str) -> bool:
    """Verifica hash."""
    try:
        ph.verify(hash, password)
        # Rehash se necessário (parâmetros mudaram)
        if ph.check_needs_rehash(hash):
            return hash_password(password)
        return True
    except VerifyMismatchError:
        return False
```

**Dados Sensíveis (Fernet):**

```python
from cryptography.fernet import Fernet

# Gerar chave (uma vez, armazenar em .env)
# key = Fernet.generate_key()

FERNET_KEY = settings.FERNET_KEY.encode()
cipher = Fernet(FERNET_KEY)

def encrypt_data(plaintext: str) -> str:
    """Encripta string."""
    return cipher.encrypt(plaintext.encode()).decode()

def decrypt_data(ciphertext: str) -> str:
    """Decripta string."""
    return cipher.decrypt(ciphertext.encode()).decode()

# Uso: Encriptar CPF/CNPJ antes de salvar
user.cpf = encrypt_data("12345678900")
```

### 5.3 Rate Limiting

**Implementação com SlowAPI:**

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379"
)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Aplicar rate limit
@app.post("/api/checkout/stripe-session")
@limiter.limit("5/minute")  # 5 requests por minuto
async def create_checkout(
    request: Request,
    data: CheckoutRequest,
    user: User = Depends(get_current_user)
):
    ...
```

**Rate Limits Recomendados:**

| Endpoint | Limite | Janela |
|----------|--------|--------|
| `/api/checkout/*` | 5 | 1 minuto |
| `/api/webhooks/*` | 100 | 1 minuto |
| `/api/admin/*` | 50 | 1 minuto |
| `/api/transactions/*` | 20 | 1 minuto |

### 5.4 CORS & Headers de Segurança

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://eva.com",
        "https://app.eva.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    max_age=600  # Cache preflight por 10 min
)

# Security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
```

---

## 6. FLUXOS DE DADOS DETALHADOS

### 6.1 Fluxo: Checkout com Cartão (Stripe)

```
┌──────────┐     1. POST /checkout/stripe-session      ┌──────────┐
│  React   │ ──────────────────────────────────────────>│ FastAPI  │
│ Frontend │     Body: {plan_tier, frequency}           │ Backend  │
└──────────┘                                             └────┬─────┘
                                                              │
                                         2. stripe.checkout.Session.create()
                                                              │
                                                              v
                                                         ┌─────────┐
                                                         │ Stripe  │
                                                         │   API   │
                                                         └────┬────┘
                                                              │
     ┌────────────────────────────────────────────────────────┘
     │  3. Return session.url
     v
┌──────────┐     4. Redirect user                       ┌──────────┐
│ FastAPI  │ ──────────────────────────────────────────>│  React   │
│ Backend  │     Response: {url: checkout.stripe.com}   │ Frontend │
└──────────┘                                             └────┬─────┘
                                                              │
                                         5. User completes payment
                                                              │
                                                              v
                                                         ┌─────────┐
                                                         │ Stripe  │
                                                         │ Hosted  │
                                                         │Checkout │
                                                         └────┬────┘
                                                              │
                            6. Webhook: checkout.session.completed
                                                              │
┌──────────┐                                                  v
│ FastAPI  │ <──────────────────────────────────────────────────
│ Backend  │     POST /webhooks/stripe
└────┬─────┘     Event: {type, data: {object}}
     │
     │  7. Validate signature (HMAC)
     │  8. Create subscription in DB
     │  9. Create transaction record
     │  10. Publish to Redis (WebSocket)
     │
     v
┌──────────┐     11. WebSocket message                 ┌──────────┐
│  Redis   │ ──────────────────────────────────────────>│  React   │
│ Pub/Sub  │     {event: payment_confirmed}            │ Frontend │
└──────────┘                                            └──────────┘
```

### 6.2 Fluxo: Confirmação Manual (Wise/Nomad)

```
┌──────────┐     1. GET /checkout/instructions/wise    ┌──────────┐
│  React   │ ──────────────────────────────────────────>│ FastAPI  │
│ Frontend │     Query: ?currency=EUR                   │ Backend  │
└──────────┘                                             └────┬─────┘
                                                              │
                                         2. Query payment_instructions table
                                                              │
                                                              v
                                                         ┌──────────┐
                                                         │PostgreSQL│
                                                         └────┬─────┘
                                                              │
     ┌────────────────────────────────────────────────────────┘
     │  3. Return instructions JSON
     v
┌──────────┐     4. Display IBAN, SWIFT, etc.          ┌──────────┐
│ FastAPI  │ ──────────────────────────────────────────>│  React   │
│ Backend  │                                            │ Frontend │
└──────────┘                                            └────┬─────┘
                                                             │
                                        5. User transfers money externally
                                                             │
                                                             v
                                                        ┌─────────┐
                                                        │  Wise   │
                                                        │  Bank   │
                                                        └────┬────┘
                                                             │
                            6. User uploads receipt (PDF/image)
                                                             │
┌──────────┐     7. POST /checkout/upload-receipt       v
│  React   │ ──────────────────────────────────────────────>┌──────────┐
│ Frontend │     Multipart: file + transaction_id           │ FastAPI  │
└──────────┘                                                 │ Backend  │
                                                             └────┬─────┘
                                                                  │
                                          8. Upload to GCS (google-cloud-storage)
                                                                  │
                                                                  v
                                                             ┌─────────┐
                                                             │Google   │
                                                             │Cloud    │
                                                             │Storage  │
                                                             └────┬────┘
                                                                  │
     ┌────────────────────────────────────────────────────────────┘
     │  9. Update transaction: status=waiting_approval, proof_url
     v
┌──────────┐     10. Notify admin via email            ┌──────────┐
│PostgreSQL│ ────────────────────────────────────────> │ SendGrid │
└──────────┘                                            └──────────┘

                    --- Admin Reviews ---

┌──────────┐     11. POST /admin/approve-transaction   ┌──────────┐
│  Admin   │ ──────────────────────────────────────────>│ FastAPI  │
│  Panel   │     Body: {transaction_id}                 │ Backend  │
└──────────┘                                             └────┬─────┘
                                                              │
                                         12. Update status=paid
                                         13. Extend subscription period
                                         14. Send confirmation email
                                                              │
                                                              v
                                                         ┌──────────┐
                                                         │PostgreSQL│
                                                         └──────────┘
```

### 6.3 Fluxo: Grace Period (Celery Beat)

```
┌──────────┐     Cron: Daily at 04:00 UTC
│  Celery  │
│   Beat   │
└────┬─────┘
     │
     │  1. Trigger task: check_expired_subscriptions
     v
┌──────────┐     2. Query: WHERE current_period_end < NOW() - 1 day
│  Celery  │
│  Worker  │
└────┬─────┘
     │
     v
┌──────────┐     3. Fetch expired subscriptions
│PostgreSQL│
└────┬─────┘
     │
     │  4. For each subscription:
     │     - Calculate days_overdue
     │     - Execute reminder action
     v
┌──────────────────────────────────────────────────┐
│  Reminder Logic (Escalating)                    │
│                                                  │
│  Day +1:  Send email (SendGrid)                │
│  Day +3:  Send WhatsApp (Twilio)               │
│  Day +7:  Send Push (Firebase FCM)             │
│  Day +10: Soft Block → status=past_due         │
│           Middleware restricts API access       │
│  Day +30: Hard Block → status=canceled         │
│           Redirect to renewal page              │
└──────────────────────────────────────────────────┘
```

---

## 7. CÓDIGO DE REFERÊNCIA

### 7.1 Endpoint Completo: Checkout Stripe

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.checkout import StripeCheckoutRequest, StripeCheckoutResponse
from app.services.payment.stripe import StripePaymentService
from app.dependencies import get_current_user, get_db
from app.models.user import User

router = APIRouter(prefix="/api/checkout", tags=["Checkout"])

@router.post(
    "/stripe-session",
    response_model=StripeCheckoutResponse,
    status_code=201
)
async def create_stripe_checkout_session(
    data: StripeCheckoutRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cria sessão de checkout do Stripe.
    
    **Flow:**
    1. Valida plano e frequência
    2. Cria Stripe Checkout Session
    3. Retorna URL para redirect
    
    **Rate Limit:** 5/minute
    """
    # Validar plano
    valid_plans = ["gold", "diamond"]
    if data.plan_tier not in valid_plans:
        raise HTTPException(400, f"Invalid plan. Must be one of: {valid_plans}")
    
    # Inicializar service
    stripe_service = StripePaymentService(db)
    
    try:
        # Criar sessão
        session_data = await stripe_service.create_checkout_session(
            user_id=user.id,
            plan_tier=data.plan_tier,
            frequency=data.frequency,
            success_url=f"{settings.FRONTEND_URL}/payment/success",
            cancel_url=f"{settings.FRONTEND_URL}/payment/cancel"
        )
        
        return StripeCheckoutResponse(
            url=session_data["url"],
            session_id=session_data["session_id"],
            expires_at=session_data["expires_at"]
        )
    
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error(f"Stripe checkout error: {e}", extra={"user_id": user.id})
        raise HTTPException(500, "Failed to create checkout session")
```

### 7.2 Service Layer: Stripe

```python
from typing import Dict
from datetime import datetime, timedelta
import stripe
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripePaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_checkout_session(
        self,
        user_id: int,
        plan_tier: str,
        frequency: str,
        success_url: str,
        cancel_url: str
    ) -> Dict[str, any]:
        """
        Cria Stripe Checkout Session.
        
        Returns:
            {
                "url": "https://checkout.stripe.com/...",
                "session_id": "cs_test_...",
                "expires_at": 1705320000
            }
        """
        # Map plan → price_id
        price_map = {
            ("gold", "monthly"): settings.STRIPE_PRICE_GOLD_MONTHLY,
            ("gold", "yearly"): settings.STRIPE_PRICE_GOLD_YEARLY,
            ("diamond", "monthly"): settings.STRIPE_PRICE_DIAMOND_MONTHLY,
            ("diamond", "yearly"): settings.STRIPE_PRICE_DIAMOND_YEARLY,
        }
        
        price_id = price_map.get((plan_tier, frequency))
        if not price_id:
            raise ValueError(f"Invalid plan configuration: {plan_tier}/{frequency}")
        
        # Criar sessão
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=f"{success_url}?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=cancel_url,
            client_reference_id=str(user_id),
            metadata={
                "user_id": str(user_id),
                "plan_tier": plan_tier,
                "frequency": frequency
            },
            subscription_data={
                "metadata": {"user_id": str(user_id)}
            },
            expires_at=int((datetime.utcnow() + timedelta(hours=1)).timestamp())
        )
        
        return {
            "url": session.url,
            "session_id": session.id,
            "expires_at": session.expires_at
        }
```

### 7.3 Webhook Handler

```python
from fastapi import APIRouter, Request, HTTPException
import stripe
from app.core.config import settings
from app.tasks.payment import process_stripe_webhook

router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])

@router.post("/stripe")
async def stripe_webhook(request: Request):
    """
    Recebe webhooks do Stripe.
    
    **Security:** Valida signature com HMAC SHA-256
    """
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")
    
    try:
        # Validar signature
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(400, "Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(400, "Invalid signature")
    
    # Processar async com Celery
    await process_stripe_webhook.delay(event.to_dict())
    
    return {"received": True}
```

### 7.4 Celery Task: Processar Webhook

```python
from celery import shared_task
from app.core.database import AsyncSessionLocal
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.transaction import Transaction, TransactionStatus
from datetime import datetime, timedelta

@shared_task(bind=True, max_retries=3)
async def process_stripe_webhook(self, event: dict):
    """
    Processa eventos Stripe de forma assíncrona.
    
    **Retry Policy:** 3 tentativas com exponential backoff
    """
    event_type = event["type"]
    
    async with AsyncSessionLocal() as db:
        try:
            if event_type == "checkout.session.completed":
                await _handle_checkout_completed(db, event)
            
            elif event_type == "invoice.paid":
                await _handle_invoice_paid(db, event)
            
            elif event_type == "invoice.payment_failed":
                await _handle_payment_failed(db, event)
            
            elif event_type == "customer.subscription.deleted":
                await _handle_subscription_canceled(db, event)
            
            await db.commit()
        
        except Exception as e:
            await db.rollback()
            logger.error(f"Webhook processing error: {e}", extra={"event_type": event_type})
            raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))

async def _handle_checkout_completed(db, event):
    """Ativa subscription após checkout."""
    session = event["data"]["object"]
    user_id = int(session["metadata"]["user_id"])
    
    # Criar subscription
    subscription = Subscription(
        user_id=user_id,
        plan_tier=session["metadata"]["plan_tier"],
        status=SubscriptionStatus.ACTIVE,
        payment_method_default="stripe_card",
        external_subscription_id=session["subscription"],
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow() + timedelta(days=30),
        metadata_json={"frequency": session["metadata"]["frequency"]}
    )
    db.add(subscription)
    await db.flush()
    
    # Criar transaction
    transaction = Transaction(
        subscription_id=subscription.id,
        user_id=user_id,
        amount=session["amount_total"] / 100,
        currency="BRL",
        provider="stripe",
        status=TransactionStatus.PAID,
        external_ref=session["id"]
    )
    db.add(transaction)
    
    # Publicar evento no Redis
    await redis.publish(
        f"payment:{user_id}",
        json.dumps({
            "event": "payment_confirmed",
            "subscription_id": subscription.id
        })
    )
```

---

## 8. MONITORAMENTO & OBSERVABILIDADE

### 8.1 Logging Estruturado (Structlog)

```python
import structlog
from pythonjsonlogger import jsonlogger

# Configuração
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Uso
logger.info(
    "payment_created",
    user_id=123,
    amount=59.90,
    provider="stripe",
    transaction_id=456
)
```

**Output:**
```json
{
  "event": "payment_created",
  "timestamp": "2026-01-15T10:30:00.123Z",
  "level": "info",
  "logger": "app.services.payment",
  "user_id": 123,
  "amount": 59.90,
  "provider": "stripe",
  "transaction_id": 456
}
```

### 8.2 Métricas (Prometheus)

```python
from prometheus_client import Counter, Histogram, Gauge

# Definir métricas
payment_created = Counter(
    "payment_created_total",
    "Total de pagamentos criados",
    ["provider", "plan_tier"]
)

payment_duration = Histogram(
    "payment_processing_duration_seconds",
    "Tempo de processamento de pagamentos",
    ["provider"]
)

active_subscriptions = Gauge(
    "active_subscriptions_total",
    "Subscriptions ativas por tier",
    ["plan_tier"]
)

# Uso
@payment_duration.labels(provider="stripe").time()
async def process_stripe_payment(...):
    payment_created.labels(provider="stripe", plan_tier="gold").inc()
    ...

# Endpoint de métricas
from fastapi import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
```

### 8.3 Error Tracking (Sentry)

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,  # 10% das transações
    environment=settings.ENVIRONMENT,
    release=settings.APP_VERSION
)

# Capturar erro com contexto
try:
    await process_payment(...)
except Exception as e:
    sentry_sdk.capture_exception(
        e,
        extra={
            "user_id": user.id,
            "transaction_id": transaction.id,
            "provider": "stripe"
        }
    )
    raise
```

### 8.4 Health Checks

```python
from fastapi import status
from sqlalchemy import text

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Verifica saúde do sistema.
    
    Checks:
    - Database connection
    - Redis connection
    - Celery workers
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # Database
    try:
        await db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "ok"
    except Exception as e:
        health_status["checks"]["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Redis
    try:
        await redis.ping()
        health_status["checks"]["redis"] = "ok"
    except Exception as e:
        health_status["checks"]["redis"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Celery
    try:
        celery_inspect = celery_app.control.inspect()
        active_workers = celery_inspect.active()
        health_status["checks"]["celery"] = f"{len(active_workers)} workers"
    except Exception as e:
        health_status["checks"]["celery"] = f"error: {str(e)}"
    
    if health_status["status"] == "unhealthy":
        raise HTTPException(503, health_status)
    
    return health_status
```

---

## 8.5 Monitoramento com Google Cloud Operations

**A. Cloud Logging (Structured Logs):**

```python
from google.cloud import logging
import structlog

# Inicializar Cloud Logging
logging_client = logging.Client()
logging_client.setup_logging()

# Configurar structlog para GCP
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()

# Uso com severity levels do GCP
logger.info(
    "payment_processed",
    severity="INFO",  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    user_id=123,
    amount=59.90,
    provider="stripe"
)
```

**B. Cloud Monitoring (Métricas Customizadas):**

```python
from google.cloud import monitoring_v3
from google.api import metric_pb2, label_pb2

def create_custom_metric(project_id: str):
    """
    Cria métrica customizada para pagamentos.
    """
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{project_id}"
    
    descriptor = metric_pb2.MetricDescriptor()
    descriptor.type = "custom.googleapis.com/payments/processed_total"
    descriptor.metric_kind = metric_pb2.MetricDescriptor.MetricKind.CUMULATIVE
    descriptor.value_type = metric_pb2.MetricDescriptor.ValueType.INT64
    descriptor.description = "Total de pagamentos processados"
    
    # Labels
    labels = descriptor.labels.add()
    labels.key = "provider"
    labels.value_type = label_pb2.LabelDescriptor.ValueType.STRING
    
    labels = descriptor.labels.add()
    labels.key = "status"
    labels.value_type = label_pb2.LabelDescriptor.ValueType.STRING
    
    descriptor = client.create_metric_descriptor(
        name=project_name,
        metric_descriptor=descriptor
    )
    
    return descriptor

def write_custom_metric(
    project_id: str,
    provider: str,
    status: str,
    value: int
):
    """
    Escreve valor para métrica customizada.
    """
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{project_id}"
    
    series = monitoring_v3.TimeSeries()
    series.metric.type = "custom.googleapis.com/payments/processed_total"
    series.metric.labels["provider"] = provider
    series.metric.labels["status"] = status
    
    now = time.time()
    seconds = int(now)
    nanos = int((now - seconds) * 10**9)
    interval = monitoring_v3.TimeInterval(
        {"end_time": {"seconds": seconds, "nanos": nanos}}
    )
    
    point = monitoring_v3.Point({
        "interval": interval,
        "value": {"int64_value": value}
    })
    
    series.points = [point]
    client.create_time_series(name=project_name, time_series=[series])
```

**C. Cloud Trace (Distributed Tracing):**

```python
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Setup tracing
trace.set_tracer_provider(TracerProvider())
cloud_trace_exporter = CloudTraceSpanExporter()
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(cloud_trace_exporter)
)

tracer = trace.get_tracer(__name__)

# Uso em endpoints
@app.post("/api/checkout/stripe-session")
async def create_checkout(data: CheckoutRequest):
    with tracer.start_as_current_span("create_stripe_checkout") as span:
        span.set_attribute("user_id", data.user_id)
        span.set_attribute("plan_tier", data.plan_tier)
        
        # Sua lógica aqui
        result = await stripe_service.create_session(...)
        
        span.set_attribute("session_id", result["session_id"])
        return result
```

**D. Error Reporting (integração com Sentry + GCP):**

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from google.cloud import error_reporting

# Sentry
sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
    environment=settings.ENVIRONMENT,
    release=settings.APP_VERSION
)

# Google Error Reporting
error_client = error_reporting.Client()

# Capturar erro em ambos
try:
    await process_payment(...)
except Exception as e:
    # Sentry (com contexto rico)
    sentry_sdk.capture_exception(e)
    
    # GCP Error Reporting
    error_client.report_exception()
    
    raise
```

**E. Uptime Checks (monitoramento de disponibilidade):**

```python
from google.cloud import monitoring_v3

def create_uptime_check(project_id: str):
    """
    Cria uptime check para o endpoint /health.
    """
    client = monitoring_v3.UptimeCheckServiceClient()
    project_name = f"projects/{project_id}"
    
    config = monitoring_v3.UptimeCheckConfig()
    config.display_name = "EVA API Health Check"
    config.monitored_resource.type = "uptime_url"
    config.monitored_resource.labels["host"] = "api.eva.com"
    
    config.http_check.path = "/health"
    config.http_check.port = 443
    config.http_check.use_ssl = True
    
    config.timeout = {"seconds": 10}
    config.period = {"seconds": 60}  # Check a cada 1 minuto
    
    config = client.create_uptime_check_config(
        parent=project_name,
        uptime_check_config=config
    )
    
    return config
```

**F. Alert Policies (alertas automáticos):**

```python
from google.cloud import monitoring_v3

def create_alert_policy(project_id: str):
    """
    Cria política de alerta para taxa de erro > 5%.
    """
    client = monitoring_v3.AlertPolicyServiceClient()
    project_name = f"projects/{project_id}"
    
    alert_policy = monitoring_v3.AlertPolicy()
    alert_policy.display_name = "High Error Rate"
    alert_policy.combiner = monitoring_v3.AlertPolicy.ConditionCombinerType.OR
    
    # Condição: taxa de erro > 5%
    condition = monitoring_v3.AlertPolicy.Condition()
    condition.display_name = "Error rate above 5%"
    condition.condition_threshold.filter = (
        'resource.type="cloud_run_revision" '
        'metric.type="run.googleapis.com/request_count" '
        'metric.label.response_code_class="5xx"'
    )
    condition.condition_threshold.comparison = (
        monitoring_v3.ComparisonType.COMPARISON_GT
    )
    condition.condition_threshold.threshold_value = 0.05
    condition.condition_threshold.duration = {"seconds": 300}  # 5 min
    
    alert_policy.conditions.append(condition)
    
    # Notification channels (email, SMS, Slack)
    alert_policy.notification_channels = [
        "projects/eva-project/notificationChannels/123456"
    ]
    
    alert_policy = client.create_alert_policy(
        name=project_name,
        alert_policy=alert_policy
    )
    
    return alert_policy
```

**G. Dashboard no Cloud Monitoring:**

```json
{
  "displayName": "EVA Financial Hub Dashboard",
  "mosaicLayout": {
    "columns": 12,
    "tiles": [
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Request Rate",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "resource.type=\"cloud_run_revision\" metric.type=\"run.googleapis.com/request_count\"",
                  "aggregation": {
                    "alignmentPeriod": "60s",
                    "perSeriesAligner": "ALIGN_RATE"
                  }
                }
              }
            }]
          }
        }
      },
      {
        "xPos": 6,
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Response Latency (p99)",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "resource.type=\"cloud_run_revision\" metric.type=\"run.googleapis.com/request_latencies\"",
                  "aggregation": {
                    "alignmentPeriod": "60s",
                    "perSeriesAligner": "ALIGN_DELTA",
                    "crossSeriesReducer": "REDUCE_PERCENTILE_99"
                  }
                }
              }
            }]
          }
        }
      },
      {
        "yPos": 4,
        "width": 12,
        "height": 4,
        "widget": {
          "title": "Payments by Provider",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "metric.type=\"custom.googleapis.com/payments/processed_total\"",
                  "aggregation": {
                    "alignmentPeriod": "300s",
                    "perSeriesAligner": "ALIGN_RATE",
                    "groupByFields": ["metric.label.provider"]
                  }
                }
              }
            }]
          }
        }
      }
    ]
  }
}
```

**H. Integração com Slack para Alertas:**

```python
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

slack_client = WebClient(token=settings.SLACK_BOT_TOKEN)

async def send_alert_to_slack(
    channel: str,
    severity: str,
    message: str,
    details: dict
):
    """
    Envia alerta para Slack com formatação rica.
    """
    color = {
        "INFO": "#36a64f",
        "WARNING": "#ff9900",
        "ERROR": "#ff0000",
        "CRITICAL": "#990000"
    }.get(severity, "#808080")
    
    try:
        response = slack_client.chat_postMessage(
            channel=channel,
            text=f"{severity}: {message}",
            attachments=[{
                "color": color,
                "fields": [
                    {"title": k, "value": str(v), "short": True}
                    for k, v in details.items()
                ],
                "footer": "EVA Financial Hub",
                "ts": int(datetime.utcnow().timestamp())
            }]
        )
    except SlackApiError as e:
        logger.error(f"Slack error: {e.response['error']}")
```

---

## 9. DEPLOYMENT

### 9.1 Docker Compose (Development)

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: docker/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://eva:password@postgres:5432/eva_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - ./app:/app/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  postgres:
    image: postgres:16.1-alpine
    environment:
      POSTGRES_USER: eva
      POSTGRES_PASSWORD: password
      POSTGRES_DB: eva_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7.2-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  celery_worker:
    build:
      context: .
      dockerfile: docker/Dockerfile
    command: celery -A app.core.celery_app worker --loglevel=info
    depends_on:
      - redis
      - postgres
    environment:
      - DATABASE_URL=postgresql+asyncpg://eva:password@postgres:5432/eva_db
      - REDIS_URL=redis://redis:6379/0

  celery_beat:
    build:
      context: .
      dockerfile: docker/Dockerfile
    command: celery -A app.core.celery_app beat --loglevel=info
    depends_on:
      - redis
      - postgres
    environment:
      - DATABASE_URL=postgresql+asyncpg://eva:password@postgres:5432/eva_db
      - REDIS_URL=redis://redis:6379/0

volumes:
  postgres_data:
  redis_data:
```

### 9.2 Google Cloud Platform (Production)

**Opção A: Cloud Run (Serverless - Recomendado para começar)**

```yaml
# cloudrun.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: eva-api
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "1"
        autoscaling.knative.dev/maxScale: "100"
    spec:
      containerConcurrency: 80
      containers:
      - image: gcr.io/eva-project/api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-secrets
              key: url
        - name: REDIS_URL
          value: "redis://10.0.0.3:6379"
        resources:
          limits:
            cpu: "2"
            memory: "2Gi"
```

**Deploy para Cloud Run:**

```bash
# Build com Cloud Build
gcloud builds submit --tag gcr.io/eva-project/api:latest

# Deploy
gcloud run deploy eva-api \
  --image gcr.io/eva-project/api:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=postgresql://... \
  --vpc-connector vpc-connector-name \
  --max-instances 100 \
  --cpu 2 \
  --memory 2Gi \
  --timeout 300
```

**Opção B: Google Kubernetes Engine (GKE - Para escala enterprise)**

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: eva-api
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: eva-api
  template:
    metadata:
      labels:
        app: eva-api
    spec:
      containers:
      - name: api
        image: gcr.io/eva-project/api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: url
        resources:
          requests:
            cpu: "500m"
            memory: "512Mi"
          limits:
            cpu: "2"
            memory: "2Gi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: eva-api-service
spec:
  type: LoadBalancer
  selector:
    app: eva-api
  ports:
  - port: 80
    targetPort: 8000
```

**Deploy para GKE:**

```bash
# Criar cluster
gcloud container clusters create eva-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n1-standard-2 \
  --enable-autoscaling \
  --min-nodes 3 \
  --max-nodes 10

# Configurar kubectl
gcloud container clusters get-credentials eva-cluster --zone us-central1-a

# Deploy
kubectl apply -f k8s/
```

**Opção C: Cloud SQL + Cloud Memorystore (Managed Services)**

```bash
# Criar Cloud SQL (PostgreSQL)
gcloud sql instances create eva-db \
  --database-version=POSTGRES_16 \
  --tier=db-custom-4-16384 \
  --region=us-central1 \
  --storage-size=100GB \
  --storage-auto-increase \
  --backup-start-time=03:00

# Criar banco
gcloud sql databases create eva_production --instance=eva-db

# Criar usuário
gcloud sql users create eva_user \
  --instance=eva-db \
  --password=secure_password

# Criar Cloud Memorystore (Redis)
gcloud redis instances create eva-redis \
  --size=5 \
  --region=us-central1 \
  --tier=standard \
  --redis-version=redis_7_0
```

### 9.3 Nginx Configuration (Production)

```nginx
upstream fastapi_backend {
    server api:8000;
}

server {
    listen 80;
    server_name api.eva.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.eva.com;

    ssl_certificate /etc/letsencrypt/live/api.eva.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.eva.com/privkey.pem;
    ssl_protocols TLSv1.3;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/m;
    limit_req zone=api_limit burst=20 nodelay;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;

    location / {
        proxy_pass http://fastapi_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /ws {
        proxy_pass http://fastapi_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

---

## 10. CHECKLIST DE IMPLEMENTAÇÃO

### Fase 1: Infraestrutura (Semana 1-2)
- [ ] Setup PostgreSQL com schema inicial
- [ ] Setup Redis para cache/queue
- [ ] Configurar Alembic para migrations
- [ ] Implementar logging estruturado
- [ ] Configurar Docker Compose

### Fase 2: Core API (Semana 3-4)
- [ ] Implementar autenticação JWT
- [ ] Criar modelos SQLAlchemy
- [ ] Implementar endpoints de checkout
- [ ] Integrar Stripe SDK
- [ ] Integrar Asaas API
- [ ] Testes unitários (>80% coverage)

### Fase 3: Webhooks & Async (Semana 5)
- [ ] Implementar validação de webhooks
- [ ] Configurar Celery workers
- [ ] Criar tasks para processamento assíncrono
- [ ] Implementar retry logic
- [ ] Testes de integração

### Fase 4: Bitcoin & Internacional (Semana 6)
- [ ] Integrar OpenNode/BTCPay
- [ ] Implementar conversão BRL→BTC
- [ ] Criar fluxo Wise/Nomad
- [ ] Implementar upload S3
- [ ] Painel admin para aprovações

### Fase 5: Observabilidade (Semana 7)
- [ ] Integrar Prometheus metrics
- [ ] Configurar Sentry
- [ ] Implementar health checks
- [ ] Dashboard Grafana
- [ ] Alertas (PagerDuty/Opsgenie)

### Fase 6: Frontend (Semana 8-9)
- [ ] Setup React + TypeScript
- [ ] Implementar componente PaymentSelector
- [ ] Integrar Stripe Elements
- [ ] QR Code display (Pix/Bitcoin)
- [ ] Upload de comprovante
- [ ] Testes E2E (Cypress)

### Fase 7: Produção (Semana 10)
- [ ] Configurar Kubernetes/ECS
- [ ] Setup Nginx + Let's Encrypt
- [ ] Configurar CI/CD
- [ ] Backup automático DB
- [ ] Documentação API (OpenAPI)
- [ ] Load testing (Locust)

### Fase 8: CI/CD com Google Cloud Build (Semana 11)
- [ ] Configurar Cloud Build triggers
- [ ] Pipeline de testes automatizados
- [ ] Deploy automático para Cloud Run/GKE
- [ ] Rollback automático em caso de erro
- [ ] Monitoramento de deploys

---

## 11. CI/CD COM GOOGLE CLOUD BUILD

### 11.1 Cloud Build Configuration

**cloudbuild.yaml:**

```yaml
steps:
  # 1. Install dependencies
  - name: 'python:3.11'
    entrypoint: 'pip'
    args: ['install', '-r', 'requirements.txt', '--user']
  
  # 2. Run tests
  - name: 'python:3.11'
    entrypoint: 'pytest'
    args: ['tests/', '--cov=app', '--cov-report=xml']
    env:
      - 'DATABASE_URL=postgresql://test:test@localhost/test_db'
  
  # 3. Build Docker image
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - 'gcr.io/$PROJECT_ID/eva-api:$COMMIT_SHA'
      - '-t'
      - 'gcr.io/$PROJECT_ID/eva-api:latest'
      - '.'
  
  # 4. Push to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - 'gcr.io/$PROJECT_ID/eva-api:$COMMIT_SHA'
  
  # 5. Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: 'gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'eva-api'
      - '--image=gcr.io/$PROJECT_ID/eva-api:$COMMIT_SHA'
      - '--region=us-central1'
      - '--platform=managed'
      - '--allow-unauthenticated'
  
  # 6. Run smoke tests
  - name: 'gcr.io/cloud-builders/curl'
    args:
      - '-f'
      - 'https://eva-api-xxx.run.app/health'

images:
  - 'gcr.io/$PROJECT_ID/eva-api:$COMMIT_SHA'
  - 'gcr.io/$PROJECT_ID/eva-api:latest'

options:
  machineType: 'N1_HIGHCPU_8'
  logging: CLOUD_LOGGING_ONLY

timeout: '1200s'
```

### 11.2 Multi-Stage Dockerfile (Otimizado para GCP)

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application
COPY ./app ./app

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Environment
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 11.3 GitHub Actions Integration

**.github/workflows/deploy.yml:**

```yaml
name: Deploy to GCP

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

env:
  PROJECT_ID: eva-project
  SERVICE_NAME: eva-api
  REGION: us-central1

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
      
      redis:
        image: redis:7
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379/0
        run: |
          pytest tests/ --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Authenticate to GCP
        uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      
      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v1
      
      - name: Build and push to GCR
        run: |
          gcloud builds submit \
            --tag gcr.io/$PROJECT_ID/$SERVICE_NAME:$GITHUB_SHA \
            --tag gcr.io/$PROJECT_ID/$SERVICE_NAME:latest
      
      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy $SERVICE_NAME \
            --image gcr.io/$PROJECT_ID/$SERVICE_NAME:$GITHUB_SHA \
            --platform managed \
            --region $REGION \
            --allow-unauthenticated \
            --set-env-vars DATABASE_URL=${{ secrets.DATABASE_URL }} \
            --set-env-vars REDIS_URL=${{ secrets.REDIS_URL }}
      
      - name: Smoke test
        run: |
          SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
            --region $REGION \
            --format 'value(status.url)')
          
          curl -f $SERVICE_URL/health || exit 1
```

### 11.4 Rollback Strategy

**Script de rollback automático:**

```bash
#!/bin/bash
# rollback.sh

SERVICE_NAME="eva-api"
REGION="us-central1"

# Get current revision
CURRENT=$(gcloud run services describe $SERVICE_NAME \
  --region $REGION \
  --format 'value(status.latestReadyRevisionName)')

echo "Current revision: $CURRENT"

# Get previous revision
PREVIOUS=$(gcloud run revisions list \
  --service $SERVICE_NAME \
  --region $REGION \
  --limit 2 \
  --format 'value(name)' | tail -n 1)

echo "Rolling back to: $PREVIOUS"

# Rollback
gcloud run services update-traffic $SERVICE_NAME \
  --region $REGION \
  --to-revisions $PREVIOUS=100

echo "Rollback completed!"
```

### 11.5 Blue-Green Deployment

```bash
#!/bin/bash
# blue-green-deploy.sh

SERVICE_NAME="eva-api"
REGION="us-central1"
NEW_IMAGE="gcr.io/eva-project/eva-api:$COMMIT_SHA"

# Deploy new revision (0% traffic)
gcloud run deploy $SERVICE_NAME \
  --image $NEW_IMAGE \
  --region $REGION \
  --no-traffic \
  --tag blue

# Get new revision URL
BLUE_URL=$(gcloud run services describe $SERVICE_NAME \
  --region $REGION \
  --format 'value(status.traffic[0].url)')

# Smoke test on blue
if curl -f "$BLUE_URL/health"; then
  echo "Blue environment healthy, switching traffic..."
  
  # Gradual traffic shift: 10% -> 50% -> 100%
  gcloud run services update-traffic $SERVICE_NAME \
    --region $REGION \
    --to-tags blue=10,green=90
  
  sleep 60
  
  gcloud run services update-traffic $SERVICE_NAME \
    --region $REGION \
    --to-tags blue=50,green=50
  
  sleep 60
  
  gcloud run services update-traffic $SERVICE_NAME \
    --region $REGION \
    --to-tags blue=100
  
  echo "Deployment completed!"
else
  echo "Blue environment unhealthy, aborting deployment"
  exit 1
fi
```

---

## 12. VARIÁVEIS DE AMBIENTE

```bash
# .env.example

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/eva_db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=

# JWT
JWT_PRIVATE_KEY_PATH=keys/private.pem
JWT_PUBLIC_KEY_PATH=keys/public.pem
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Encryption
FERNET_KEY=your_fernet_key_here

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_GOLD_MONTHLY=price_xxx
STRIPE_PRICE_GOLD_YEARLY=price_yyy
STRIPE_PRICE_DIAMOND_MONTHLY=price_zzz
STRIPE_PRICE_DIAMOND_YEARLY=price_aaa

# Asaas
ASAAS_API_KEY=your_api_key
ASAAS_WEBHOOK_TOKEN=your_webhook_token
ASAAS_ENVIRONMENT=sandbox  # ou production

# OpenNode
OPENNODE_API_KEY=your_api_key
OPENNODE_WEBHOOK_SECRET=your_webhook_secret

# Google Cloud Platform
GCP_PROJECT_ID=your-project-id
GCS_BUCKET_NAME=eva-receipts
GCS_CREDENTIALS_PATH=path/to/service-account-key.json
# Ou usar GOOGLE_APPLICATION_CREDENTIALS env var
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json

# SendGrid
SENDGRID_API_KEY=your_api_key
SENDGRID_FROM_EMAIL=noreply@eva.com

# Twilio
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_FROM=+14155238886

# Sentry
SENTRY_DSN=https://xxx@sentry.io/yyy
SENTRY_ENVIRONMENT=production

# App
APP_NAME=EVA Financial Hub
APP_VERSION=3.0.0
API_BASE_URL=https://api.eva.com
FRONTEND_URL=https://app.eva.com
ENVIRONMENT=production  # ou development
DEBUG=false
```

---

## 13. RECURSOS ADICIONAIS

### Documentação de Referência:
- **FastAPI:** https://fastapi.tiangolo.com/
- **SQLAlchemy 2.0:** https://docs.sqlalchemy.org/
- **Stripe API:** https://stripe.com/docs/api
- **Asaas API:** https://docs.asaas.com/
- **OpenNode API:** https://developers.opennode.com/
- **Celery:** https://docs.celeryq.dev/
- **Google Cloud Storage:** https://cloud.google.com/storage/docs
- **Google Cloud Run:** https://cloud.google.com/run/docs
- **Google Cloud SQL:** https://cloud.google.com/sql/docs
- **Google Cloud Build:** https://cloud.google.com/build/docs

### Ferramentas Recomendadas:
- **API Testing:** Bruno, Postman, httpx CLI
- **Load Testing:** Locust, k6, Apache Bench
- **Monitoring:** Google Cloud Monitoring, Grafana, Prometheus, Datadog
- **Error Tracking:** Sentry, Rollbar, Google Error Reporting
- **CI/CD:** Cloud Build, GitHub Actions, GitLab CI, CircleCI
- **Database Tools:** pgAdmin, DBeaver, DataGrip
- **GCP CLI:** gcloud, gsutil, kubectl

### Bibliotecas Python Essenciais:
```txt
# requirements.txt (versões específicas)

# Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0

# Database
sqlalchemy[asyncio]==2.0.25
asyncpg==0.29.0
alembic==1.13.1

# Redis & Queue
redis==5.0.1
celery==5.3.4
celery[redis]==5.3.4

# Payment Gateways
stripe==10.12.0
httpx==0.26.0

# Google Cloud
google-cloud-storage==2.14.0
google-cloud-logging==3.9.0
google-auth==2.27.0

# Security
pyjwt[crypto]==2.8.0
cryptography==42.0.0
argon2-cffi==23.1.0

# Monitoring
structlog==24.1.0
prometheus-client==0.19.0
sentry-sdk==1.40.0
opentelemetry-api==1.22.0

# Utils
python-multipart==0.0.6
aiofiles==23.2.1
python-dotenv==1.0.0

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
httpx==0.26.0
```

---

**Versão:** 3.0.0  
**Última Atualização:** Janeiro 2026  
**Autor:** Lu + Equipe EVA  
**Status:** Ready for Implementation

---

*Este documento é um guia técnico completo para implementação do Hub Financeiro EVA. Para dúvidas ou contribuições, entre em contato com a equipe de engenharia.*