"""
Schemas Pydantic para Webhooks
Validação de eventos de gateways de pagamento
"""
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


# ==========================================
# STRIPE WEBHOOKS
# ==========================================

class StripeWebhookEvent(BaseModel):
    """Evento de webhook Stripe"""
    id: str = Field(..., description="ID do evento")
    type: str = Field(..., description="Tipo do evento")
    data: dict = Field(..., description="Dados do evento")
    created: int = Field(..., description="Timestamp de criação")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "evt_abc123",
                "type": "checkout.session.completed",
                "data": {
                    "object": {
                        "id": "cs_test_a1b2c3",
                        "amount_total": 5990,
                        "currency": "brl",
                        "metadata": {
                            "user_id": "123",
                            "plan_tier": "gold"
                        }
                    }
                },
                "created": 1705320000
            }
        }


# ==========================================
# ASAAS WEBHOOKS
# ==========================================

class AsaasWebhookEvent(BaseModel):
    """Evento de webhook Asaas"""
    event: str = Field(..., description="Tipo do evento")
    payment: dict = Field(..., description="Dados do pagamento")
    
    class Config:
        schema_extra = {
            "example": {
                "event": "PAYMENT_RECEIVED",
                "payment": {
                    "id": "pay_abc123",
                    "value": 59.90,
                    "status": "RECEIVED",
                    "externalReference": "user_123_1705320000"
                }
            }
        }


# ==========================================
# OPENNODE WEBHOOKS
# ==========================================

class OpenNodeWebhookEvent(BaseModel):
    """Evento de webhook OpenNode (Bitcoin)"""
    id: str = Field(..., description="ID do invoice")
    status: str = Field(..., description="Status (paid, expired, processing)")
    order_id: str = Field(..., description="Order ID (nossa referência)")
    amount: float = Field(..., description="Valor em satoshis")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "abc123",
                "status": "paid",
                "order_id": "user_123_1705320000",
                "amount": 15000
            }
        }


# ==========================================
# GENERIC WEBHOOK RESPONSE
# ==========================================

class WebhookProcessedResponse(BaseModel):
    """Response padrao para webhooks"""
    received: bool = Field(True, description="Webhook recebido")
    event_id: Optional[str] = Field(None, description="ID do evento")
    message: Optional[str] = Field(None, description="Mensagem adicional")
    queued: bool = Field(True, description="Indica se foi enfileirado para processamento async")
    processed_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp de recebimento")

    class Config:
        schema_extra = {
            "example": {
                "received": True,
                "event_id": "evt_abc123",
                "message": "Webhook queued for processing",
                "queued": True,
                "processed_at": "2026-01-25T10:00:00Z"
            }
        }
