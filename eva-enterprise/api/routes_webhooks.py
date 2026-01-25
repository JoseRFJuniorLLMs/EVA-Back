"""
Rotas de Webhooks
Endpoints para receber confirmacoes de pagamento dos gateways.

IMPORTANTE: Webhooks sao processados de forma ASSINCRONA via Celery.
O endpoint retorna imediatamente e o processamento ocorre em background.

Isso garante:
- Resposta rapida ao gateway (evita timeout)
- Retry automatico em caso de falha
- Melhor escalabilidade
"""
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import json

from database.connection import get_db
from schemas.webhook import WebhookProcessedResponse
from services.payment import StripePaymentService, AsaasPaymentService, OpenNodePaymentService, WisePaymentService
from services.webhook_service import WebhookService
import os

# Celery Tasks
from tasks.webhook_tasks import (
    process_stripe_webhook,
    process_asaas_webhook,
    process_opennode_webhook,
    process_wise_webhook,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


# ==========================================
# STRIPE WEBHOOK
# ==========================================

@router.post("/stripe", response_model=WebhookProcessedResponse)
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Recebe webhooks do Stripe.

    **Eventos processados (via Celery):**
    - `checkout.session.completed` - Pagamento inicial
    - `invoice.paid` - Renovacao bem-sucedida
    - `invoice.payment_failed` - Falha no pagamento
    - `customer.subscription.deleted` - Cancelamento
    - `customer.subscription.updated` - Alteracao de plano

    **Seguranca:**
    - Validacao de assinatura HMAC SHA-256
    - Idempotencia baseada em event.id

    **Processamento:**
    - Webhook e validado e retornado imediatamente
    - Processamento real ocorre em background via Celery

    **Rate Limit:** 100/minuto
    """
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    if not sig_header:
        raise HTTPException(400, detail="Missing Stripe-Signature header")

    try:
        # Validar assinatura ANTES de enfileirar
        stripe_service = StripePaymentService()
        event = stripe_service.verify_webhook_signature(
            payload=payload,
            signature=sig_header,
            webhook_secret=webhook_secret
        )

        event_type = event["type"]
        event_id = event["id"]

        logger.info(
            f"Stripe webhook received - queueing for async processing",
            extra={"event_type": event_type, "event_id": event_id}
        )

        # Disparar task Celery para processamento assincrono
        process_stripe_webhook.delay(event)

        # Retornar imediatamente para o Stripe
        return WebhookProcessedResponse(
            received=True,
            event_id=event_id,
            message="Webhook queued for processing"
        )

    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        raise HTTPException(400, detail="Invalid payload")
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(400, detail="Invalid signature")


# ==========================================
# ASAAS WEBHOOK
# ==========================================

@router.post("/asaas", response_model=WebhookProcessedResponse)
async def asaas_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Recebe webhooks do Asaas (Pix).

    **Eventos processados (via Celery):**
    - `PAYMENT_RECEIVED` - Pix recebido
    - `PAYMENT_OVERDUE` - Vencido
    - `PAYMENT_REFUNDED` - Estornado

    **Seguranca:**
    - Validacao de token fixo

    **Rate Limit:** 100/minuto
    """
    # Asaas envia token em query param ou header
    token = request.query_params.get("token") or request.headers.get("asaas-access-token")

    asaas_service = AsaasPaymentService()
    if not asaas_service.verify_webhook_token(token):
        raise HTTPException(401, detail="Invalid token")

    try:
        payload = await request.json()
        event_type = payload.get("event")

        logger.info(
            f"Asaas webhook received - queueing for async processing",
            extra={"event_type": event_type}
        )

        # Disparar task Celery para processamento assincrono
        process_asaas_webhook.delay(payload)

        return WebhookProcessedResponse(
            received=True,
            message="Webhook queued for processing"
        )

    except Exception as e:
        logger.error(f"Asaas webhook error: {e}")
        raise HTTPException(400, detail="Invalid payload")


# ==========================================
# OPENNODE WEBHOOK (BITCOIN)
# ==========================================

@router.post("/opennode", response_model=WebhookProcessedResponse)
async def opennode_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Recebe webhooks do OpenNode (Bitcoin Lightning).

    **Eventos processados (via Celery):**
    - `paid` - Invoice pago
    - `expired` - Invoice expirou (15 min)
    - `processing` - Confirmacao em andamento

    **Seguranca:**
    - Validacao de assinatura HMAC SHA-256

    **Rate Limit:** 100/minuto
    """
    payload = await request.body()
    signature = request.headers.get("opennode-signature")

    if not signature:
        raise HTTPException(400, detail="Missing signature")

    try:
        opennode_service = OpenNodePaymentService()

        # Validar assinatura ANTES de enfileirar
        is_valid = opennode_service.verify_webhook_signature(
            payload=payload,
            signature=signature
        )

        if not is_valid:
            raise HTTPException(401, detail="Invalid signature")

        data = json.loads(payload)
        status = data.get("status")
        order_id = data.get("order_id")

        logger.info(
            f"OpenNode webhook received - queueing for async processing",
            extra={"status": status, "order_id": order_id}
        )

        # Disparar task Celery para processamento assincrono
        process_opennode_webhook.delay(data)

        return WebhookProcessedResponse(
            received=True,
            message="Webhook queued for processing"
        )

    except Exception as e:
        logger.error(f"OpenNode webhook error: {e}")
        raise HTTPException(400, detail="Webhook processing error")

# ==========================================
# WISE WEBHOOK
# ==========================================

@router.post("/wise", response_model=WebhookProcessedResponse)
async def wise_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Recebe notificacao de depositos da Wise.

    **Processamento (via Celery):**
    - Webhook dispara task de reconciliacao
    - Reconciliacao busca transacoes e cruza com referencias pendentes
    """
    try:
        payload = await request.json()
        event_type = payload.get("event_type")  # Ex: balances#credit

        logger.info(f"Wise webhook received - queueing for async processing: {event_type}")

        # Disparar task Celery para processamento assincrono
        process_wise_webhook.delay(payload)

        return WebhookProcessedResponse(
            received=True,
            message="Webhook queued for processing"
        )

    except Exception as e:
        logger.error(f"Wise webhook error: {e}")
        return WebhookProcessedResponse(received=True)
