"""
Payment Tasks
Tasks assíncronas para processamento de pagamentos e assinaturas
"""
from core.celery_app import celery_app
from services.payment import StripePaymentService
from services.payment.wise_service import WisePaymentService
from database.connection import AsyncSessionLocal
import os
import logging
import asyncio

logger = logging.getLogger(__name__)

# Helper para executar async code dentro do Celery (sync)
def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@celery_app.task(name="api.tasks.payment.process_stripe_webhook")
def process_stripe_webhook_task(event_data: dict):
    """
    Task para processar webhook Stripe em background.
    Idempotência deve ser garantida pelo service.
    """
    event_type = event_data.get("type")
    event_id = event_data.get("id")
    
    logger.info(f"[Task] Processing Stripe event {event_id}: {event_type}")
    
    # Simulação de processamento pesado
    # Na prática, chamaria o service para atualizar DB
    # Como os services usam async/await e SQLAlchemy async, 
    # precisaríamos de uma sessão de DB separada aqui.
    
    if event_type == "checkout.session.completed":
        session = event_data["data"]["object"]
        user_id = session.get("metadata", {}).get("user_id")
        logger.info(f"[Task] Activating subscription for user {user_id}")
        # TODO: Implementar lógica de DB
        
    return {"status": "processed", "event_id": event_id}

@celery_app.task(name="api.tasks.payment.check_expired_subscriptions")
def check_expired_subscriptions():
    """
    Cron job para verificar assinaturas expiradas.
    """
    logger.info("[Cron] Checking expired subscriptions...")
    
    # 1. Buscar subscriptions where current_period_end < NOW() AND status = 'active'
    # 2. Atualizar para 'past_due' (grace period) ou 'canceled'
    # 3. Enviar email de aviso
    
    return "Checked subscriptions"

@celery_app.task(name="api.tasks.payment.send_renewal_reminder")
def send_renewal_reminder(user_id: int):
    """
    Envia lembrete de renovação.
    """
    logger.info(f"[Task] Sending renewal reminder to user {user_id}")
    # TODO: Enviar email (SendGrid/AWS SES)

@celery_app.task(name="api.tasks.payment.poll_wise_transactions")
def poll_wise_transactions_task():
    """
    Cron job: Busca depósitos na Wise a cada X minutos.
    Backup para caso o Webhook falhe.
    """
    logger.info("[Cron] Polling Wise transactions...")
    
    async def _process():
        try:
            async with AsyncSessionLocal() as db:
                service = WisePaymentService(db)
                profile_id = os.getenv("WISE_PROFILE_ID")
                
                if profile_id:
                    await service.reconcile_transactions(int(profile_id))
                else:
                    logger.warning("WISE_PROFILE_ID not configured")
        except Exception as e:
            logger.error(f"Error in Wise polling: {e}")
    
    run_async(_process())
    return "Wise Polling Completed"
