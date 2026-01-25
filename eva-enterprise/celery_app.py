"""
Celery Configuration for EVA Enterprise
========================================
Configuracao do Celery com Redis para processamento assincrono de:
- Webhooks de pagamento (Stripe, Asaas, OpenNode, Wise)
- Notificacoes push
- Tarefas de reconciliacao
- Jobs agendados (cron)
"""
import os
from celery import Celery
from kombu import Queue, Exchange
from dotenv import load_dotenv

load_dotenv()

# Redis Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)

# Create Celery app
celery_app = Celery(
    "eva_enterprise",
    broker=REDIS_URL,
    backend=CELERY_RESULT_BACKEND,
    include=[
        "tasks.webhook_tasks",
        "tasks.notification_tasks",
        "tasks.reconciliation_tasks",
        "tasks.scheduled_tasks",
    ]
)

# Celery Configuration
celery_app.conf.update(
    # Task Settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,

    # Task Execution
    task_acks_late=True,  # Acknowledge after task completes (safer)
    task_reject_on_worker_lost=True,  # Requeue if worker dies
    task_time_limit=300,  # 5 minutes max per task
    task_soft_time_limit=240,  # Soft limit (4 min) to allow cleanup

    # Worker Settings
    worker_prefetch_multiplier=1,  # Fair distribution
    worker_concurrency=4,  # Adjust based on server
    worker_max_tasks_per_child=100,  # Restart worker after 100 tasks (memory leak prevention)

    # Result Backend
    result_expires=3600,  # Results expire after 1 hour
    result_extended=True,  # Store task args in result

    # Retry Settings
    task_default_retry_delay=60,  # 1 minute between retries
    task_max_retries=5,

    # Beat Scheduler (for cron jobs)
    beat_schedule={
        # Reconciliacao de transacoes a cada 15 minutos
        "reconcile-wise-transactions": {
            "task": "tasks.reconciliation_tasks.reconcile_wise_transactions",
            "schedule": 900.0,  # 15 minutes
        },
        # Limpar transacoes pendentes antigas
        "cleanup-pending-transactions": {
            "task": "tasks.scheduled_tasks.cleanup_pending_transactions",
            "schedule": 3600.0,  # 1 hour
        },
        # Verificar assinaturas a vencer
        "check-expiring-subscriptions": {
            "task": "tasks.scheduled_tasks.check_expiring_subscriptions",
            "schedule": 86400.0,  # 24 hours
        },
        # Health check do sistema de pagamentos
        "payment-health-check": {
            "task": "tasks.scheduled_tasks.payment_health_check",
            "schedule": 300.0,  # 5 minutes
        },
    },

    # Queues
    task_queues=(
        Queue("default", Exchange("default"), routing_key="default"),
        Queue("webhooks", Exchange("webhooks"), routing_key="webhooks.#"),
        Queue("notifications", Exchange("notifications"), routing_key="notifications.#"),
        Queue("reconciliation", Exchange("reconciliation"), routing_key="reconciliation.#"),
        Queue("scheduled", Exchange("scheduled"), routing_key="scheduled.#"),
    ),

    # Task Routes
    task_routes={
        "tasks.webhook_tasks.*": {"queue": "webhooks"},
        "tasks.notification_tasks.*": {"queue": "notifications"},
        "tasks.reconciliation_tasks.*": {"queue": "reconciliation"},
        "tasks.scheduled_tasks.*": {"queue": "scheduled"},
    },
)


# Optional: Error handling hooks
@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery connection."""
    print(f"Request: {self.request!r}")
    return {"status": "ok", "worker": self.request.hostname}
