"""
Schemas Pydantic para Subscriptions
Validação de assinaturas e histórico
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from decimal import Decimal


class SubscriptionBase(BaseModel):
    """Base para Subscription"""
    plan_tier: Literal["basic", "gold", "diamond"]
    status: Literal["active", "past_due", "canceled", "trialing"]


class SubscriptionCreate(BaseModel):
    """Criar nova assinatura"""
    user_id: int = Field(..., description="ID do usuário")
    plan_tier: Literal["gold", "diamond"] = Field(..., description="Plano")
    payment_method: str = Field(..., description="Método de pagamento")
    frequency: Literal["monthly", "yearly"] = Field(..., description="Frequência")
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": 123,
                "plan_tier": "gold",
                "payment_method": "stripe_card",
                "frequency": "monthly"
            }
        }


class SubscriptionResponse(BaseModel):
    """Response com dados da assinatura"""
    id: int
    user_id: int
    plan_tier: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    payment_method_default: Optional[str]
    days_remaining: Optional[float]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "user_id": 123,
                "plan_tier": "gold",
                "status": "active",
                "current_period_start": "2026-01-15T00:00:00Z",
                "current_period_end": "2026-02-15T00:00:00Z",
                "payment_method_default": "stripe_card",
                "days_remaining": 30.5,
                "created_at": "2026-01-15T10:00:00Z",
                "updated_at": "2026-01-15T10:00:00Z"
            }
        }


class SubscriptionUpdate(BaseModel):
    """Atualizar assinatura"""
    status: Optional[Literal["active", "past_due", "canceled"]] = None
    payment_method_default: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "status": "canceled"
            }
        }


class SubscriptionCancelRequest(BaseModel):
    """Request para cancelar assinatura"""
    reason: Optional[str] = Field(None, description="Motivo do cancelamento")
    immediate: bool = Field(False, description="Cancelar imediatamente ou no fim do período")
    
    class Config:
        schema_extra = {
            "example": {
                "reason": "Não preciso mais do serviço",
                "immediate": False
            }
        }


class SubscriptionHistoryItem(BaseModel):
    """Item do histórico de assinatura"""
    id: int
    plan_tier: str
    status: str
    started_at: datetime
    ended_at: Optional[datetime]
    total_paid: Decimal
    transactions_count: int
    
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "plan_tier": "gold",
                "status": "canceled",
                "started_at": "2025-12-01T00:00:00Z",
                "ended_at": "2026-01-01T00:00:00Z",
                "total_paid": "59.90",
                "transactions_count": 1
            }
        }
