# Celery Tasks - EVA Enterprise

Sistema de processamento assincrono para webhooks de pagamento e tarefas agendadas.

## Requisitos

- Redis Server (local ou remoto)
- Python 3.9+
- Dependencias instaladas (`pip install -r requirements.txt`)

## Configuracao

Adicione as variaveis no `.env`:

```env
# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Banco de dados (sincrono)
DATABASE_URL_SYNC=postgresql://user:pass@localhost:5432/eva_db
```

## Executando

### 1. Iniciar Redis

```bash
# Docker
docker run -d --name eva-redis -p 6379:6379 redis:7-alpine

# Ou instalar localmente
# Windows: usar Memurai ou WSL
# Linux: sudo apt install redis-server && sudo service redis start
```

### 2. Iniciar Worker Celery

```bash
cd eva-enterprise

# Worker principal (todas as filas)
celery -A celery_app worker --loglevel=INFO

# Workers especializados (producao)
celery -A celery_app worker -Q webhooks --loglevel=INFO --concurrency=4
celery -A celery_app worker -Q notifications --loglevel=INFO --concurrency=2
celery -A celery_app worker -Q reconciliation --loglevel=INFO --concurrency=1
celery -A celery_app worker -Q scheduled --loglevel=INFO --concurrency=1
```

### 3. Iniciar Beat Scheduler (tarefas agendadas)

```bash
celery -A celery_app beat --loglevel=INFO
```

### 4. Monitorar com Flower (opcional)

```bash
pip install flower
celery -A celery_app flower --port=5555
# Acesse http://localhost:5555
```

## Arquitetura

```
eva-enterprise/
├── celery_app.py          # Configuracao do Celery
├── tasks/
│   ├── __init__.py        # Exports
│   ├── webhook_tasks.py   # Tasks de webhooks
│   ├── notification_tasks.py  # Tasks de notificacao
│   ├── reconciliation_tasks.py  # Tasks de reconciliacao
│   └── scheduled_tasks.py # Tasks agendadas (cron)
```

## Tasks Disponiveis

### Webhook Tasks

| Task | Descricao |
|------|-----------|
| `process_stripe_webhook` | Processa eventos Stripe |
| `process_asaas_webhook` | Processa eventos Asaas (Pix) |
| `process_opennode_webhook` | Processa eventos OpenNode (Bitcoin) |
| `process_wise_webhook` | Processa eventos Wise |

### Notification Tasks

| Task | Descricao |
|------|-----------|
| `send_push_notification` | Envia push para um dispositivo |
| `send_multicast_notification` | Envia push para multiplos dispositivos |
| `send_payment_confirmation_notification` | Notifica confirmacao de pagamento |
| `send_subscription_expiring_notification` | Notifica assinatura expirando |
| `send_emergency_alert` | Alerta de emergencia para cuidadores |
| `send_medication_reminder` | Lembrete de medicamento |

### Reconciliation Tasks

| Task | Descricao |
|------|-----------|
| `reconcile_wise_transactions` | Reconcilia transacoes Wise |
| `reconcile_all_pending_transactions` | Reconcilia todas as pendentes |

### Scheduled Tasks (Cron)

| Task | Intervalo | Descricao |
|------|-----------|-----------|
| `cleanup_pending_transactions` | 1 hora | Limpa transacoes antigas |
| `check_expiring_subscriptions` | 24 horas | Verifica assinaturas expirando |
| `payment_health_check` | 5 minutos | Health check do sistema |
| `reconcile_wise_transactions` | 15 minutos | Reconciliacao Wise |

## Filas

| Fila | Workers | Uso |
|------|---------|-----|
| `default` | 2 | Tasks gerais |
| `webhooks` | 4 | Webhooks de pagamento (prioridade alta) |
| `notifications` | 2 | Push notifications |
| `reconciliation` | 1 | Reconciliacao de transacoes |
| `scheduled` | 1 | Tarefas agendadas |

## Exemplo de Uso

```python
from tasks import process_stripe_webhook, send_push_notification

# Disparar task imediatamente
process_stripe_webhook.delay(event_data)

# Disparar com delay de 5 segundos
send_push_notification.apply_async(
    args=[token, "Titulo", "Mensagem"],
    countdown=5
)

# Agendar para horario especifico
from datetime import datetime, timedelta
eta = datetime.utcnow() + timedelta(hours=1)
send_push_notification.apply_async(
    args=[token, "Titulo", "Mensagem"],
    eta=eta
)
```

## Troubleshooting

### Worker nao conecta ao Redis

```bash
# Verificar se Redis esta rodando
redis-cli ping  # Deve retornar PONG

# Verificar conexao
python -c "import redis; r = redis.Redis(); print(r.ping())"
```

### Tasks nao sao executadas

1. Verificar se worker esta rodando
2. Verificar logs do worker
3. Verificar se a fila correta esta sendo consumida

### Conexao com banco falha

```bash
# Verificar DATABASE_URL_SYNC (nao deve ter +asyncpg)
# Correto: postgresql://user:pass@host:5432/db
# Errado: postgresql+asyncpg://user:pass@host:5432/db
```

## Docker Compose (Producao)

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  celery-worker:
    build: .
    command: celery -A celery_app worker -Q webhooks,notifications --loglevel=INFO
    environment:
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL_SYNC=postgresql://...
    depends_on:
      - redis

  celery-beat:
    build: .
    command: celery -A celery_app beat --loglevel=INFO
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis

  flower:
    build: .
    command: celery -A celery_app flower --port=5555
    ports:
      - "5555:5555"
    depends_on:
      - redis

volumes:
  redis_data:
```

## Metricas e Monitoramento

- **Flower**: Dashboard web para monitorar workers e tasks
- **Redis**: Usar `redis-cli info` para metricas
- **Logs**: Configurar logging estruturado para analise

---

**EVA Enterprise** - Celery Tasks v1.0
