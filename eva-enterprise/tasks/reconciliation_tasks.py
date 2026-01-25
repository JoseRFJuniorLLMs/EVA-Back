"""
Reconciliation Tasks
====================
Tasks Celery para reconciliacao de transacoes.

Reconciliacao = verificar transacoes pendentes e sincronizar com gateways.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from celery import shared_task
from sqlalchemy import select, and_

from database.connection_sync import get_sync_db
from database.payment_models import Transaction, Subscription, PaymentInstruction

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    name="tasks.reconciliation_tasks.reconcile_wise_transactions"
)
def reconcile_wise_transactions(self, profile_id: Optional[int] = None) -> Dict:
    """
    Reconcilia transacoes Wise buscando depositos recebidos.

    1. Busca transacoes recentes via Wise API
    2. Cruza com payment_instructions pendentes pelo reference_code
    3. Marca como pagas se encontrar match
    """
    logger.info(f"Starting Wise reconciliation (profile: {profile_id})")

    try:
        with get_sync_db() as db:
            # Buscar instrucoes pendentes
            stmt = select(PaymentInstruction).where(
                and_(
                    PaymentInstruction.provider == "wise",
                    PaymentInstruction.status == "pending"
                )
            )
            result = db.execute(stmt)
            pending_instructions = result.scalars().all()

            if not pending_instructions:
                logger.info("No pending Wise instructions to reconcile")
                return {"status": "no_pending", "checked": 0}

            logger.info(f"Found {len(pending_instructions)} pending Wise instructions")

            # Importar Wise service
            from services.payment.wise_service import WisePaymentService
            wise_service = WisePaymentService(db)

            matched = 0
            for instruction in pending_instructions:
                reference_code = instruction.reference_code

                # Verificar se o reference_code foi usado em algum deposito
                try:
                    is_paid = wise_service.check_reference_status_sync(reference_code)

                    if is_paid:
                        # Marcar instrucao como usada
                        instruction.status = "used"
                        instruction.updated_at = datetime.utcnow()

                        # Processar pagamento associado
                        if instruction.transaction_id:
                            trans_stmt = select(Transaction).where(
                                Transaction.id == instruction.transaction_id
                            )
                            trans_result = db.execute(trans_stmt)
                            transaction = trans_result.scalar_one_or_none()

                            if transaction and transaction.status != "paid":
                                transaction.status = "paid"
                                transaction.updated_at = datetime.utcnow()

                                # Atualizar assinatura
                                if transaction.subscription_id:
                                    sub_stmt = select(Subscription).where(
                                        Subscription.id == transaction.subscription_id
                                    )
                                    sub_result = db.execute(sub_stmt)
                                    subscription = sub_result.scalar_one_or_none()

                                    if subscription:
                                        subscription.status = "active"
                                        now = datetime.utcnow()
                                        subscription.current_period_end = now + timedelta(days=30)
                                        subscription.updated_at = now

                                matched += 1
                                logger.info(f"Wise payment matched: {reference_code}")

                except Exception as e:
                    logger.warning(f"Error checking reference {reference_code}: {e}")
                    continue

            db.commit()

            return {
                "status": "completed",
                "checked": len(pending_instructions),
                "matched": matched
            }

    except Exception as e:
        logger.error(f"Wise reconciliation error: {e}")
        raise


@shared_task(
    bind=True,
    max_retries=3,
    name="tasks.reconciliation_tasks.reconcile_all_pending_transactions"
)
def reconcile_all_pending_transactions(self) -> Dict:
    """
    Reconcilia todas as transacoes pendentes de todos os providers.
    """
    logger.info("Starting full transaction reconciliation")

    results = {
        "stripe": 0,
        "asaas": 0,
        "opennode": 0,
        "wise": 0,
        "errors": []
    }

    try:
        with get_sync_db() as db:
            # Buscar transacoes pendentes com mais de 5 minutos
            cutoff = datetime.utcnow() - timedelta(minutes=5)
            stmt = select(Transaction).where(
                and_(
                    Transaction.status == "pending",
                    Transaction.created_at < cutoff
                )
            )
            result = db.execute(stmt)
            pending = result.scalars().all()

            logger.info(f"Found {len(pending)} pending transactions to check")

            for transaction in pending:
                provider = transaction.provider
                external_ref = transaction.external_ref

                try:
                    if provider == "stripe":
                        # Verificar status no Stripe
                        from services.payment.stripe_service import StripePaymentService
                        stripe_service = StripePaymentService()
                        status = stripe_service.get_session_status(external_ref)

                        if status == "complete":
                            transaction.status = "paid"
                            transaction.updated_at = datetime.utcnow()
                            results["stripe"] += 1

                    elif provider == "asaas":
                        # Verificar status no Asaas
                        from services.payment.asaas_service import AsaasPaymentService
                        asaas_service = AsaasPaymentService()
                        status = asaas_service.get_payment_status(external_ref)

                        if status == "RECEIVED":
                            transaction.status = "paid"
                            transaction.updated_at = datetime.utcnow()
                            results["asaas"] += 1

                    elif provider == "opennode":
                        # Verificar status no OpenNode
                        from services.payment.opennode_service import OpenNodePaymentService
                        opennode_service = OpenNodePaymentService()
                        status = opennode_service.get_charge_status(external_ref)

                        if status == "paid":
                            transaction.status = "paid"
                            transaction.updated_at = datetime.utcnow()
                            results["opennode"] += 1
                        elif status == "expired":
                            transaction.status = "expired"
                            transaction.updated_at = datetime.utcnow()

                except Exception as e:
                    logger.warning(f"Error reconciling transaction {transaction.id}: {e}")
                    results["errors"].append({
                        "transaction_id": transaction.id,
                        "error": str(e)
                    })

            db.commit()

            # Disparar reconciliacao Wise separadamente
            reconcile_wise_transactions.delay()
            results["wise"] = "triggered"

            logger.info(f"Reconciliation completed: {results}")
            return results

    except Exception as e:
        logger.error(f"Full reconciliation error: {e}")
        raise


@shared_task(
    bind=True,
    max_retries=2,
    name="tasks.reconciliation_tasks.verify_subscription_payments"
)
def verify_subscription_payments(self, subscription_id: int) -> Dict:
    """
    Verifica se uma assinatura tem todos os pagamentos em dia.
    """
    logger.info(f"Verifying payments for subscription {subscription_id}")

    try:
        with get_sync_db() as db:
            # Buscar assinatura
            stmt = select(Subscription).where(Subscription.id == subscription_id)
            result = db.execute(stmt)
            subscription = result.scalar_one_or_none()

            if not subscription:
                return {"status": "not_found"}

            # Buscar ultima transacao paga
            trans_stmt = select(Transaction).where(
                and_(
                    Transaction.subscription_id == subscription_id,
                    Transaction.status == "paid"
                )
            ).order_by(Transaction.created_at.desc()).limit(1)

            trans_result = db.execute(trans_stmt)
            last_payment = trans_result.scalar_one_or_none()

            if not last_payment:
                return {
                    "status": "no_payments",
                    "subscription_status": subscription.status
                }

            # Verificar se o periodo ainda e valido
            now = datetime.utcnow()
            is_valid = (
                subscription.current_period_end and
                subscription.current_period_end > now
            )

            return {
                "status": "verified",
                "is_valid": is_valid,
                "last_payment": str(last_payment.created_at),
                "expires_at": str(subscription.current_period_end) if subscription.current_period_end else None
            }

    except Exception as e:
        logger.error(f"Subscription verification error: {e}")
        raise
