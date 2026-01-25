"""
Webhook Tasks
=============
Tasks Celery para processamento assincrono de webhooks de pagamento.

Beneficios:
- Resposta imediata ao gateway (evita timeout)
- Retry automatico em caso de falha
- Processamento paralelo de multiplos webhooks
- Logs detalhados para debug
"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError

from database.connection_sync import get_sync_db
from database.payment_models import Transaction, Subscription, WebhookLog
from database.models import Usuario as User
from sqlalchemy import select, update
from datetime import timedelta

logger = logging.getLogger(__name__)


def log_webhook_event(
    db,
    provider: str,
    event_type: str,
    event_id: str,
    payload: dict,
    status: str = "received",
    error: str = None
):
    """Registra evento de webhook no banco para auditoria."""
    try:
        log_entry = WebhookLog(
            provider=provider,
            event_type=event_type,
            event_id=event_id,
            payload=payload,
            status=status,
            error_message=error,
            created_at=datetime.utcnow()
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to log webhook event: {e}")


def process_payment_confirmation_sync(
    db,
    external_ref: str,
    provider: str,
    amount: float = None
) -> bool:
    """
    Processa confirmacao de pagamento de forma sincrona.

    1. Localiza transacao pelo external_ref
    2. Marca como paga
    3. Ativa/Renova assinatura
    4. Atualiza tier do usuario
    """
    try:
        # 1. Buscar transacao
        stmt = select(Transaction).where(Transaction.external_ref == external_ref)
        result = db.execute(stmt)
        transaction = result.scalar_one_or_none()

        if not transaction:
            logger.error(f"Transaction not found for ref: {external_ref}")
            return False

        if transaction.status == "paid":
            logger.info(f"Transaction {external_ref} already paid - skipping")
            return True

        # 2. Atualizar Transacao
        transaction.status = "paid"
        transaction.updated_at = datetime.utcnow()
        transaction.provider = provider
        if amount:
            transaction.amount_received = amount

        # 3. Buscar Assinatura
        sub_stmt = select(Subscription).where(Subscription.id == transaction.subscription_id)
        sub_result = db.execute(sub_stmt)
        subscription = sub_result.scalar_one_or_none()

        if not subscription:
            logger.error(f"Subscription not found for transaction {transaction.id}")
            db.commit()
            return False

        # 4. Atualizar Assinatura (Renovacao)
        metadata = subscription.metadata_json or {}
        frequency = metadata.get("frequency", "monthly")
        days_to_add = 365 if frequency == "yearly" else 30

        now = datetime.utcnow()
        start_date = now
        if subscription.current_period_end and subscription.current_period_end > now:
            start_date = subscription.current_period_end

        new_end_date = start_date + timedelta(days=days_to_add)

        subscription.status = "active"
        subscription.current_period_end = new_end_date
        subscription.updated_at = now

        # 5. Atualizar Usuario (Tier)
        user_id = getattr(subscription, "user_id", None) or transaction.user_id
        if user_id:
            user_stmt = select(User).where(User.id == user_id)
            user_result = db.execute(user_stmt)
            user = user_result.scalar_one_or_none()

            if user:
                user.subscription_tier = subscription.plan_tier
                logger.info(f"User {user.id} upgraded to {subscription.plan_tier}")

        db.commit()

        logger.info(
            f"Payment processed successfully",
            extra={
                "external_ref": external_ref,
                "provider": provider,
                "subscription_id": subscription.id,
                "new_end_date": str(new_end_date)
            }
        )
        return True

    except Exception as e:
        logger.error(f"Error processing payment confirmation: {e}")
        db.rollback()
        return False


def process_payment_failure_sync(db, external_ref: str, reason: str = None):
    """Marca transacao como falha e registra motivo."""
    try:
        stmt = select(Transaction).where(Transaction.external_ref == external_ref)
        result = db.execute(stmt)
        transaction = result.scalar_one_or_none()

        if transaction:
            transaction.status = "failed"
            transaction.failure_reason = reason
            transaction.updated_at = datetime.utcnow()
            db.commit()
            logger.warning(f"Transaction {external_ref} marked as failed: {reason}")
    except Exception as e:
        logger.error(f"Error marking payment as failed: {e}")
        db.rollback()


# ==========================================
# STRIPE WEBHOOK TASK
# ==========================================

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    max_retries=5,
    acks_late=True,
    name="tasks.webhook_tasks.process_stripe_webhook"
)
def process_stripe_webhook(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processa webhook do Stripe de forma assincrona.

    Args:
        event_data: Evento completo do Stripe (dict)

    Returns:
        dict: Status do processamento
    """
    event_type = event_data.get("type", "unknown")
    event_id = event_data.get("id", "unknown")

    logger.info(f"Processing Stripe webhook: {event_type} ({event_id})")

    try:
        with get_sync_db() as db:
            # Log do evento
            log_webhook_event(db, "stripe", event_type, event_id, event_data, "processing")

            if event_type == "checkout.session.completed":
                session = event_data.get("data", {}).get("object", {})
                external_ref = session.get("id")
                amount = session.get("amount_total", 0) / 100  # Stripe usa centavos

                success = process_payment_confirmation_sync(
                    db, external_ref, "stripe", amount
                )

                if success:
                    # Disparar notificacao
                    from tasks.notification_tasks import send_payment_confirmation_notification
                    user_id = session.get("metadata", {}).get("user_id")
                    if user_id:
                        send_payment_confirmation_notification.delay(
                            int(user_id), "stripe", amount
                        )

                log_webhook_event(
                    db, "stripe", event_type, event_id, event_data,
                    "processed" if success else "failed"
                )

                return {"status": "processed", "event_type": event_type}

            elif event_type == "invoice.paid":
                invoice = event_data.get("data", {}).get("object", {})
                subscription_id = invoice.get("subscription")
                amount = invoice.get("amount_paid", 0) / 100

                # Para renovacoes, usar subscription_id como referencia
                success = process_payment_confirmation_sync(
                    db, subscription_id, "stripe", amount
                )

                log_webhook_event(
                    db, "stripe", event_type, event_id, event_data,
                    "processed" if success else "failed"
                )

                return {"status": "processed", "event_type": event_type}

            elif event_type == "invoice.payment_failed":
                invoice = event_data.get("data", {}).get("object", {})
                subscription_id = invoice.get("subscription")
                failure_reason = invoice.get("last_payment_error", {}).get("message", "Unknown")

                process_payment_failure_sync(db, subscription_id, failure_reason)
                log_webhook_event(
                    db, "stripe", event_type, event_id, event_data, "processed"
                )

                return {"status": "processed", "event_type": event_type, "action": "marked_failed"}

            elif event_type == "customer.subscription.deleted":
                subscription = event_data.get("data", {}).get("object", {})
                stripe_sub_id = subscription.get("id")

                # Cancelar assinatura no nosso sistema
                stmt = select(Subscription).where(
                    Subscription.stripe_subscription_id == stripe_sub_id
                )
                result = db.execute(stmt)
                sub = result.scalar_one_or_none()

                if sub:
                    sub.status = "cancelled"
                    sub.cancelled_at = datetime.utcnow()
                    db.commit()
                    logger.info(f"Subscription {stripe_sub_id} cancelled")

                log_webhook_event(
                    db, "stripe", event_type, event_id, event_data, "processed"
                )

                return {"status": "processed", "event_type": event_type, "action": "cancelled"}

            else:
                # Evento nao tratado, apenas log
                log_webhook_event(db, "stripe", event_type, event_id, event_data, "ignored")
                return {"status": "ignored", "event_type": event_type}

    except Exception as e:
        logger.error(f"Stripe webhook processing failed: {e}")
        try:
            with get_sync_db() as db:
                log_webhook_event(
                    db, "stripe", event_type, event_id, event_data,
                    "error", str(e)
                )
        except:
            pass
        raise  # Re-raise for retry


# ==========================================
# ASAAS WEBHOOK TASK (PIX)
# ==========================================

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=5,
    name="tasks.webhook_tasks.process_asaas_webhook"
)
def process_asaas_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processa webhook do Asaas (Pix) de forma assincrona.
    """
    event_type = payload.get("event", "unknown")
    payment = payload.get("payment", {})
    payment_id = payment.get("id", "unknown")

    logger.info(f"Processing Asaas webhook: {event_type} ({payment_id})")

    try:
        with get_sync_db() as db:
            log_webhook_event(db, "asaas", event_type, payment_id, payload, "processing")

            if event_type == "PAYMENT_RECEIVED":
                external_ref = payment_id
                amount = payment.get("value", 0)

                success = process_payment_confirmation_sync(
                    db, external_ref, "asaas", amount
                )

                if success:
                    from tasks.notification_tasks import send_payment_confirmation_notification
                    # Buscar user_id da transacao
                    stmt = select(Transaction).where(Transaction.external_ref == external_ref)
                    result = db.execute(stmt)
                    trans = result.scalar_one_or_none()
                    if trans:
                        send_payment_confirmation_notification.delay(
                            trans.user_id, "pix", amount
                        )

                log_webhook_event(
                    db, "asaas", event_type, payment_id, payload,
                    "processed" if success else "failed"
                )

                return {"status": "processed", "event_type": event_type}

            elif event_type == "PAYMENT_OVERDUE":
                process_payment_failure_sync(db, payment_id, "Payment overdue")
                log_webhook_event(db, "asaas", event_type, payment_id, payload, "processed")
                return {"status": "processed", "action": "marked_overdue"}

            elif event_type == "PAYMENT_REFUNDED":
                # Marcar como reembolsado
                stmt = select(Transaction).where(Transaction.external_ref == payment_id)
                result = db.execute(stmt)
                trans = result.scalar_one_or_none()
                if trans:
                    trans.status = "refunded"
                    trans.updated_at = datetime.utcnow()
                    db.commit()

                log_webhook_event(db, "asaas", event_type, payment_id, payload, "processed")
                return {"status": "processed", "action": "refunded"}

            else:
                log_webhook_event(db, "asaas", event_type, payment_id, payload, "ignored")
                return {"status": "ignored", "event_type": event_type}

    except Exception as e:
        logger.error(f"Asaas webhook processing failed: {e}")
        raise


# ==========================================
# OPENNODE WEBHOOK TASK (BITCOIN)
# ==========================================

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=5,
    name="tasks.webhook_tasks.process_opennode_webhook"
)
def process_opennode_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processa webhook do OpenNode (Bitcoin Lightning).
    """
    status = payload.get("status", "unknown")
    invoice_id = payload.get("id", "unknown")
    order_id = payload.get("order_id")

    logger.info(f"Processing OpenNode webhook: {status} ({invoice_id})")

    try:
        with get_sync_db() as db:
            log_webhook_event(db, "opennode", status, invoice_id, payload, "processing")

            if status == "paid":
                # OpenNode confirma pagamento
                amount_btc = payload.get("amount", 0)
                amount_fiat = payload.get("fiat_value", 0)

                success = process_payment_confirmation_sync(
                    db, invoice_id, "opennode", amount_fiat
                )

                if success:
                    from tasks.notification_tasks import send_payment_confirmation_notification
                    stmt = select(Transaction).where(Transaction.external_ref == invoice_id)
                    result = db.execute(stmt)
                    trans = result.scalar_one_or_none()
                    if trans:
                        send_payment_confirmation_notification.delay(
                            trans.user_id, "bitcoin", amount_fiat
                        )

                log_webhook_event(
                    db, "opennode", status, invoice_id, payload,
                    "processed" if success else "failed"
                )

                return {"status": "processed", "btc_amount": amount_btc}

            elif status == "expired":
                process_payment_failure_sync(db, invoice_id, "Invoice expired")
                log_webhook_event(db, "opennode", status, invoice_id, payload, "processed")
                return {"status": "processed", "action": "expired"}

            elif status == "processing":
                # Pagamento em confirmacao (aguardando confirmacoes blockchain)
                log_webhook_event(db, "opennode", status, invoice_id, payload, "pending")
                return {"status": "pending", "message": "Awaiting confirmations"}

            else:
                log_webhook_event(db, "opennode", status, invoice_id, payload, "ignored")
                return {"status": "ignored"}

    except Exception as e:
        logger.error(f"OpenNode webhook processing failed: {e}")
        raise


# ==========================================
# WISE WEBHOOK TASK
# ==========================================

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
    name="tasks.webhook_tasks.process_wise_webhook"
)
def process_wise_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processa webhook da Wise (transferencias internacionais).
    """
    event_type = payload.get("event_type", "unknown")

    logger.info(f"Processing Wise webhook: {event_type}")

    try:
        with get_sync_db() as db:
            log_webhook_event(db, "wise", event_type, "n/a", payload, "processing")

            if event_type == "balances#credit":
                # Credito recebido - disparar reconciliacao
                data = payload.get("data", {})
                resource = data.get("resource", {})
                profile_id = resource.get("profile_id")

                if profile_id:
                    from tasks.reconciliation_tasks import reconcile_wise_transactions
                    reconcile_wise_transactions.delay(profile_id)

                    log_webhook_event(db, "wise", event_type, "n/a", payload, "triggered_reconciliation")
                    return {"status": "triggered_reconciliation", "profile_id": profile_id}

                log_webhook_event(db, "wise", event_type, "n/a", payload, "no_profile_id")
                return {"status": "no_action", "reason": "no profile_id"}

            else:
                log_webhook_event(db, "wise", event_type, "n/a", payload, "ignored")
                return {"status": "ignored", "event_type": event_type}

    except Exception as e:
        logger.error(f"Wise webhook processing failed: {e}")
        raise
