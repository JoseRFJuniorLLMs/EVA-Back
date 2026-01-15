"""
Schemas Pydantic para Transactions
Validação de transações e histórico de pagamentos
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from decimal import Decimal


class TransactionBase(BaseModel):
    """Base para Transaction"""
    amount: Decimal = Field(..., gt=0, description="Valor (deve ser > 0)")
    currency: str = Field(..., max_length=3, description="Moeda (BRL, USD, EUR, BTC)")
    provider: Literal["stripe", "asaas", "opennode", "wise", "nomad"]


class TransactionCreate(BaseModel):
    """Criar nova transação"""
    user_id: int
    subscription_id: Optional[int] = None
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="BRL", max_length=3)
    provider: Literal["stripe", "asaas", "opennode", "wise", "nomad"]
    external_ref: Optional[str] = None
    metadata_json: Optional[dict] = None
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": 123,
                "subscription_id": 1,
                "amount": "59.90",
                "currency": "BRL",
                "provider": "stripe",
                "external_ref": "cs_test_a1b2c3"
            }
        }


class TransactionResponse(BaseModel):
    """Response com dados da transação"""
    id: int
    user_id: int
    subscription_id: Optional[int]
    amount: Decimal
    currency: str
    provider: str
    status: str
    external_ref: Optional[str]
    proof_url: Optional[str]
    failure_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "user_id": 123,
                "subscription_id": 1,
                "amount": "59.90",
                "currency": "BRL",
                "provider": "stripe",
                "status": "paid",
                "external_ref": "cs_test_a1b2c3",
                "proof_url": None,
                "failure_reason": None,
                "created_at": "2026-01-15T10:00:00Z",
                "updated_at": "2026-01-15T10:05:00Z"
            }
        }


class TransactionStatusUpdate(BaseModel):
    """Atualizar status de transação"""
    status: Literal["pending", "paid", "failed", "waiting_approval", "refunded"]
    failure_reason: Optional[str] = None
    external_ref: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "status": "paid",
                "external_ref": "pi_abc123"
            }
        }


class TransactionListResponse(BaseModel):
    """Lista de transações com paginação"""
    transactions: list[TransactionResponse]
    total: int
    page: int
    page_size: int
    
    class Config:
        schema_extra = {
            "example": {
                "transactions": [],
                "total": 10,
                "page": 1,
                "page_size": 20
            }
        }


class TransactionStatsResponse(BaseModel):
    """Estatísticas de transações"""
    total_transactions: int
    total_amount: Decimal
    successful_count: int
    failed_count: int
    pending_count: int
    success_rate: float
    
    class Config:
        schema_extra = {
            "example": {
                "total_transactions": 100,
                "total_amount": "5990.00",
                "successful_count": 95,
                "failed_count": 3,
                "pending_count": 2,
                "success_rate": 95.0
            }
        }
