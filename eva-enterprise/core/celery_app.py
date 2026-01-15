"""
Celery Configuration
Configuração do task queue para processamento assíncrono
"""
from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

# Obter URL do Redis ou usar localhost
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Inicializa Celery app
celery_app = Celery(
    "eva_enterprise",
    broker=REDIS_URL,
    backend=REDIS_URL
)

# Configurações do Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Rate Limits
    task_default_rate_limit="100/m",
    # Rotas para tasks (opcional, para filas separadas)
    task_routes={
        "api.tasks.payment.*": {"queue": "payments"},
        "api.tasks.notifications.*": {"queue": "notifications"},
    },
    # Cron Jobs (Beats)
    beat_schedule={
        "check-expired-subscriptions": {
            "task": "api.tasks.payment.check_expired_subscriptions",
            "schedule": 86400.0,  # Diário
        },
        "generate-monthly-report": {
            "task": "api.tasks.reports.generate_monthly_report",
            "schedule": 2592000.0,  # Mensal (aprox)
        },
        "poll-wise-payments": {
            "task": "api.tasks.payment.poll_wise_transactions",
            "schedule": 600.0, # 10 minutos
        },
    }
)

# Auto-discovery de tasks
celery_app.autodiscover_tasks([
    "api.tasks.payment",
    "api.tasks.notifications",
    "api.tasks.reports"
])
