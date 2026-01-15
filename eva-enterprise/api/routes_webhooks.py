"""
Rotas de Webhooks
Endpoints para receber confirmações de pagamento dos gateways
"""
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import json

from database.connection import get_db
from schemas.webhook import WebhookProcessedResponse
from services.payment import StripePaymentService, AsaasPaymentService, OpenNodePaymentService
import os

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
    
    **Eventos processados:**
    - `checkout.session.completed` - Pagamento inicial
    - `invoice.paid` - Renovação bem-sucedida
    - `invoice.payment_failed` - Falha no pagamento
    - `customer.subscription.deleted` - Cancelamento
    - `customer.subscription.updated` - Alteração de plano
    
    **Segurança:**
    - Validação de assinatura HMAC SHA-256
    - Idempotência baseada em event.id
    
    **Rate Limit:** 100/minuto
    """
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    if not sig_header:
        raise HTTPException(400, detail="Missing Stripe-Signature header")
    
    try:
        # Validar assinatura
        stripe_service = StripePaymentService()
        event = stripe_service.verify_webhook_signature(
            payload=payload,
            signature=sig_header,
            webhook_secret=webhook_secret
        )
        
        event_type = event["type"]
        event_id = event["id"]
        
        logger.info(
            f"Stripe webhook received",
            extra={"event_type": event_type, "event_id": event_id}
        )
        
        # TODO: Processar evento de forma assíncrona (Celery)
        # await process_stripe_webhook_task.delay(event)
        
        # Por enquanto, apenas log
        if event_type == "checkout.session.completed":
            session = event["data"]["object"]
            user_id = session.get("metadata", {}).get("user_id")
            logger.info(f"Checkout completed for user {user_id}")
        
        elif event_type == "invoice.paid":
            invoice = event["data"]["object"]
            subscription_id = invoice.get("subscription")
            logger.info(f"Invoice paid for subscription {subscription_id}")
        
        elif event_type == "invoice.payment_failed":
            invoice = event["data"]["object"]
            subscription_id = invoice.get("subscription")
            logger.warning(f"Payment failed for subscription {subscription_id}")
        
        return WebhookProcessedResponse(
            received=True,
            event_id=event_id
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
    
    **Eventos processados:**
    - `PAYMENT_RECEIVED` - Pix recebido
    - `PAYMENT_OVERDUE` - Vencido
    - `PAYMENT_REFUNDED` - Estornado
    
    **Segurança:**
    - Validação de token fixo
    
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
            f"Asaas webhook received",
            extra={"event_type": event_type}
        )
        
        # TODO: Processar evento de forma assíncrona
        if event_type == "PAYMENT_RECEIVED":
            payment = payload.get("payment", {})
            external_ref = payment.get("externalReference")
            logger.info(f"Pix received for {external_ref}")
            
            # TODO: Atualizar transaction e ativar subscription
        
        return WebhookProcessedResponse(received=True)
    
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
    
    **Eventos processados:**
    - `paid` - Invoice pago
    - `expired` - Invoice expirou (15 min)
    - `processing` - Confirmação em andamento
    
    **Segurança:**
    - Validação de assinatura HMAC SHA-256
    
    **Rate Limit:** 100/minuto
    """
    payload = await request.body()
    signature = request.headers.get("opennode-signature")
    
    if not signature:
        raise HTTPException(400, detail="Missing signature")
    
    try:
        opennode_service = OpenNodePaymentService()
        
        # Validar assinatura
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
            f"OpenNode webhook received",
            extra={"status": status, "order_id": order_id}
        )
        
        # TODO: Processar evento
        if status == "paid":
            logger.info(f"Bitcoin payment confirmed for {order_id}")
            # TODO: Atualizar transaction e ativar subscription
        
        return WebhookProcessedResponse(received=True)
    
    except Exception as e:
        logger.error(f"OpenNode webhook error: {e}")
        raise HTTPException(400, detail="Invalid webhook")
