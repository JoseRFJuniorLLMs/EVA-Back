"""
Scheduled Tasks
===============
Tasks Celery agendadas (cron jobs) para manutencao do sistema.

Agendamento configurado em celery_app.py via beat_schedule.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List

from celery import shared_task
from sqlalchemy import select, and_, delete

from database.connection_sync import get_sync_db
from database.payment_models import Transaction, Subscription, WebhookLog

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    name="tasks.scheduled_tasks.cleanup_pending_transactions"
)
def cleanup_pending_transactions(self) -> Dict:
    """
    Limpa transacoes pendentes antigas.

    - Transacoes pendentes > 24h -> expired
    - Transacoes expiradas > 7 dias -> deleted (optional)
    - Webhook logs > 30 dias -> deleted
    """
    logger.info("Starting pending transactions cleanup")

    try:
        with get_sync_db() as db:
            now = datetime.utcnow()
            expired_count = 0
            deleted_logs = 0

            # 1. Expirar transacoes pendentes > 24h
            cutoff_24h = now - timedelta(hours=24)
            stmt = select(Transaction).where(
                and_(
                    Transaction.status == "pending",
                    Transaction.created_at < cutoff_24h
                )
            )
            result = db.execute(stmt)
            old_pending = result.scalars().all()

            for trans in old_pending:
                trans.status = "expired"
                trans.updated_at = now
                trans.failure_reason = "Auto-expired after 24h"
                expired_count += 1

            # 2. Limpar webhook logs antigos (> 30 dias)
            cutoff_30d = now - timedelta(days=30)
            delete_stmt = delete(WebhookLog).where(WebhookLog.created_at < cutoff_30d)
            delete_result = db.execute(delete_stmt)
            deleted_logs = delete_result.rowcount

            db.commit()

            logger.info(f"Cleanup completed: {expired_count} expired, {deleted_logs} logs deleted")

            return {
                "status": "completed",
                "expired_transactions": expired_count,
                "deleted_logs": deleted_logs,
                "timestamp": str(now)
            }

    except Exception as e:
        logger.error(f"Cleanup error: {e}")
        raise


@shared_task(
    bind=True,
    name="tasks.scheduled_tasks.check_expiring_subscriptions"
)
def check_expiring_subscriptions(self) -> Dict:
    """
    Verifica assinaturas prestes a expirar e envia notificacoes.

    - 7 dias antes: Lembrete gentil
    - 3 dias antes: Alerta urgente
    - 1 dia antes: Ultimo aviso
    - Expirado: Suspende acesso
    """
    logger.info("Checking expiring subscriptions")

    try:
        with get_sync_db() as db:
            now = datetime.utcnow()
            notifications_sent = {
                "7_days": 0,
                "3_days": 0,
                "1_day": 0,
                "expired": 0
            }

            # Buscar assinaturas ativas
            stmt = select(Subscription).where(
                Subscription.status == "active"
            )
            result = db.execute(stmt)
            subscriptions = result.scalars().all()

            from tasks.notification_tasks import send_subscription_expiring_notification

            for sub in subscriptions:
                if not sub.current_period_end:
                    continue

                days_until_expiry = (sub.current_period_end - now).days

                if days_until_expiry < 0:
                    # Ja expirou - suspender
                    sub.status = "expired"
                    sub.updated_at = now
                    notifications_sent["expired"] += 1
                    logger.warning(f"Subscription {sub.id} expired")

                elif days_until_expiry <= 1:
                    # Ultimo dia
                    send_subscription_expiring_notification.delay(sub.user_id, 1)
                    notifications_sent["1_day"] += 1

                elif days_until_expiry <= 3:
                    # 3 dias
                    send_subscription_expiring_notification.delay(sub.user_id, days_until_expiry)
                    notifications_sent["3_days"] += 1

                elif days_until_expiry <= 7:
                    # 7 dias
                    send_subscription_expiring_notification.delay(sub.user_id, days_until_expiry)
                    notifications_sent["7_days"] += 1

            db.commit()

            logger.info(f"Expiring subscriptions check completed: {notifications_sent}")

            return {
                "status": "completed",
                "notifications": notifications_sent,
                "timestamp": str(now)
            }

    except Exception as e:
        logger.error(f"Expiring subscriptions check error: {e}")
        raise


@shared_task(
    bind=True,
    name="tasks.scheduled_tasks.payment_health_check"
)
def payment_health_check(self) -> Dict:
    """
    Verifica saude do sistema de pagamentos.

    Checks:
    - Conexao com Redis
    - Conexao com banco
    - APIs de pagamento (Stripe, Asaas, OpenNode)
    - Filas Celery
    """
    logger.info("Running payment system health check")

    health_status = {
        "timestamp": str(datetime.utcnow()),
        "database": False,
        "redis": False,
        "stripe": False,
        "asaas": False,
        "opennode": False,
        "celery_queues": {}
    }

    # 1. Check Database
    try:
        with get_sync_db() as db:
            db.execute("SELECT 1")
            health_status["database"] = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")

    # 2. Check Redis (via Celery)
    try:
        from celery_app import celery_app
        celery_app.control.ping(timeout=5)
        health_status["redis"] = True
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")

    # 3. Check Stripe
    try:
        from services.payment.stripe_service import StripePaymentService
        stripe = StripePaymentService()
        # Simples verificacao de API key
        if stripe.stripe:
            health_status["stripe"] = True
    except Exception as e:
        logger.error(f"Stripe health check failed: {e}")

    # 4. Check Asaas
    try:
        from services.payment.asaas_service import AsaasPaymentService
        asaas = AsaasPaymentService()
        if asaas.api_key:
            health_status["asaas"] = True
    except Exception as e:
        logger.error(f"Asaas health check failed: {e}")

    # 5. Check OpenNode
    try:
        from services.payment.opennode_service import OpenNodePaymentService
        opennode = OpenNodePaymentService()
        if opennode.api_key:
            health_status["opennode"] = True
    except Exception as e:
        logger.error(f"OpenNode health check failed: {e}")

    # 6. Check Celery Queues
    try:
        from celery_app import celery_app
        inspect = celery_app.control.inspect()

        active = inspect.active()
        reserved = inspect.reserved()

        if active:
            for worker, tasks in active.items():
                health_status["celery_queues"][worker] = {
                    "active": len(tasks),
                    "reserved": len(reserved.get(worker, []))
                }
    except Exception as e:
        logger.error(f"Celery queues check failed: {e}")

    # Determinar status geral
    all_healthy = all([
        health_status["database"],
        health_status["redis"],
        health_status["stripe"],
        health_status["asaas"]
    ])

    health_status["overall"] = "healthy" if all_healthy else "degraded"

    if not all_healthy:
        logger.warning(f"Payment system health degraded: {health_status}")
    else:
        logger.info("Payment system health check passed")

    return health_status


@shared_task(
    bind=True,
    name="tasks.scheduled_tasks.generate_daily_report"
)
def generate_daily_report(self) -> Dict:
    """
    Gera relatorio diario de transacoes.
    """
    logger.info("Generating daily payment report")

    try:
        with get_sync_db() as db:
            now = datetime.utcnow()
            yesterday = now - timedelta(days=1)

            # Transacoes do dia
            stmt = select(Transaction).where(
                Transaction.created_at >= yesterday
            )
            result = db.execute(stmt)
            transactions = result.scalars().all()

            # Agregar por status
            by_status = {}
            total_revenue = 0.0

            for trans in transactions:
                status = trans.status
                by_status[status] = by_status.get(status, 0) + 1

                if status == "paid":
                    total_revenue += trans.amount or 0

            # Agregar por provider
            by_provider = {}
            for trans in transactions:
                provider = trans.provider or "unknown"
                by_provider[provider] = by_provider.get(provider, 0) + 1

            report = {
                "period": {
                    "start": str(yesterday),
                    "end": str(now)
                },
                "total_transactions": len(transactions),
                "by_status": by_status,
                "by_provider": by_provider,
                "total_revenue": total_revenue,
                "generated_at": str(now)
            }

            logger.info(f"Daily report generated: {report}")

            # TODO: Enviar por email para admins
            # send_admin_email.delay("Daily Payment Report", report)

            return report

    except Exception as e:
        logger.error(f"Daily report generation error: {e}")
        raise


@shared_task(
    bind=True,
    name="tasks.scheduled_tasks.sync_subscription_tiers"
)
def sync_subscription_tiers(self) -> Dict:
    """
    Sincroniza tiers de usuarios com suas assinaturas.
    """
    logger.info("Syncing subscription tiers")

    try:
        with get_sync_db() as db:
            from database.models import Usuario as User

            # Buscar assinaturas ativas
            stmt = select(Subscription).where(
                Subscription.status == "active"
            )
            result = db.execute(stmt)
            subscriptions = result.scalars().all()

            synced = 0
            for sub in subscriptions:
                # Buscar usuario
                user_stmt = select(User).where(User.id == sub.user_id)
                user_result = db.execute(user_stmt)
                user = user_result.scalar_one_or_none()

                if user and user.subscription_tier != sub.plan_tier:
                    user.subscription_tier = sub.plan_tier
                    synced += 1
                    logger.info(f"Synced user {user.id} to tier {sub.plan_tier}")

            db.commit()

            return {
                "status": "completed",
                "synced_users": synced,
                "total_active_subscriptions": len(subscriptions)
            }

    except Exception as e:
        logger.error(f"Tier sync error: {e}")
        raise
