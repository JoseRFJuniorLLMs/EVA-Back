"""
Schemas Pydantic para Checkout
Validação de requests e responses de pagamento
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from datetime import datetime
from decimal import Decimal


# ==========================================
# STRIPE CHECKOUT
# ==========================================

class StripeCheckoutRequest(BaseModel):
    """Request para criar sessão de checkout Stripe"""
    plan_tier: Literal["gold", "diamond"] = Field(..., description="Plano: gold ou diamond")
    frequency: Literal["monthly", "yearly"] = Field(..., description="Frequência: mensal ou anual")
    success_url: Optional[str] = Field(None, description="URL de sucesso (opcional)")
    cancel_url: Optional[str] = Field(None, description="URL de cancelamento (opcional)")
    
    class Config:
        schema_extra = {
            "example": {
                "plan_tier": "gold",
                "frequency": "monthly"
            }
        }


class StripeCheckoutResponse(BaseModel):
    """Response com URL de checkout Stripe"""
    url: str = Field(..., description="URL do checkout Stripe")
    session_id: str = Field(..., description="ID da sessão")
    expires_at: int = Field(..., description="Timestamp de expiração")
    
    class Config:
        schema_extra = {
            "example": {
                "url": "https://checkout.stripe.com/c/pay/cs_test_...",
                "session_id": "cs_test_a1b2c3d4",
                "expires_at": 1705320000
            }
        }


# ==========================================
# ASAAS PIX
# ==========================================

class AsaasPixRequest(BaseModel):
    """Request para criar cobrança Pix via Asaas"""
    plan_tier: Literal["gold", "diamond"] = Field(..., description="Plano")
    frequency: Literal["monthly", "yearly"] = Field(..., description="Frequência")
    
    class Config:
        schema_extra = {
            "example": {
                "plan_tier": "gold",
                "frequency": "monthly"
            }
        }


class AsaasPixResponse(BaseModel):
    """Response com QR Code Pix"""
    charge_id: str = Field(..., description="ID da cobrança Asaas")
    qr_code_url: str = Field(..., description="URL da imagem QR Code")
    qr_code_payload: str = Field(..., description="Código Pix copia e cola")
    amount: Decimal = Field(..., description="Valor em BRL")
    expires_at: str = Field(..., description="Data de expiração")
    
    class Config:
        schema_extra = {
            "example": {
                "charge_id": "pay_abc123",
                "qr_code_url": "https://asaas.com/qr/xxx.png",
                "qr_code_payload": "00020126580014br.gov.bcb.pix...",
                "amount": "59.90",
                "expires_at": "2026-01-16T12:00:00Z"
            }
        }


# ==========================================
# BITCOIN LIGHTNING
# ==========================================

class BitcoinInvoiceRequest(BaseModel):
    """Request para criar invoice Lightning"""
    plan_tier: Literal["gold", "diamond"] = Field(..., description="Plano")
    frequency: Literal["monthly", "yearly"] = Field(..., description="Frequência")
    
    class Config:
        schema_extra = {
            "example": {
                "plan_tier": "diamond",
                "frequency": "yearly"
            }
        }


class BitcoinInvoiceResponse(BaseModel):
    """Response com invoice Lightning"""
    invoice_id: str = Field(..., description="ID do invoice")
    lightning_invoice: str = Field(..., description="Invoice Lightning (lnbc...)")
    qr_code_url: str = Field(..., description="URL do QR Code")
    amount_btc: float = Field(..., description="Valor em BTC")
    amount_brl: float = Field(..., description="Valor em BRL")
    expires_at: str = Field(..., description="Expiração (15 min)")
    
    class Config:
        schema_extra = {
            "example": {
                "invoice_id": "abc123",
                "lightning_invoice": "lnbc15u1p3xnhl2pp5jptserfk3zk4qy42tlucycrfwxhydvlemu9pqr93tuzlv9cc7g3sdq5xysxxatsyp3k7enxv4jsxqzpusp5kt...",
                "qr_code_url": "https://chart.googleapis.com/chart?chs=300x300&cht=qr&chl=lnbc...",
                "amount_btc": 0.00015,
                "amount_brl": 59.90,
                "expires_at": "2026-01-15T13:15:00Z"
            }
        }


# ==========================================
# WISE / NOMAD (INTERNACIONAL)
# ==========================================

class InternationalInstructionsRequest(BaseModel):
    """Request para obter instruções bancárias"""
    provider: Literal["wise", "nomad"] = Field(..., description="Provider")
    currency: Literal["EUR", "USD", "GBP"] = Field(..., description="Moeda")
    plan_tier: Literal["gold", "diamond"] = Field(..., description="Plano")
    frequency: Literal["monthly", "yearly"] = Field(..., description="Frequência")
    
    class Config:
        schema_extra = {
            "example": {
                "provider": "wise",
                "currency": "EUR",
                "plan_tier": "gold",
                "frequency": "monthly"
            }
        }


class InternationalInstructionsResponse(BaseModel):
    """Response com instruções bancárias"""
    provider: str = Field(..., description="Provider (wise/nomad)")
    currency: str = Field(..., description="Moeda")
    amount: Decimal = Field(..., description="Valor a transferir")
    reference_code: str = Field(..., description="Código de referência ÚNICO")
    bank_details: dict = Field(..., description="Detalhes bancários")
    instructions: list[str] = Field(..., description="Instruções passo a passo")
    
    class Config:
        schema_extra = {
            "example": {
                "provider": "wise",
                "currency": "EUR",
                "amount": "49.90",
                "reference_code": "EVA-123-1705320000",
                "bank_details": {
                    "account_holder": "EVA Payments Ltd",
                    "iban": "DE89370400440532013000",
                    "swift": "COBADEFF",
                    "bank_name": "Commerzbank AG"
                },
                "instructions": [
                    "Faça transferência para a conta acima",
                    "Use o código de referência: EVA-123-1705320000",
                    "Envie comprovante após transferência"
                ]
            }
        }


# ==========================================
# UPLOAD DE COMPROVANTE
# ==========================================

class ReceiptUploadResponse(BaseModel):
    """Response após upload de comprovante"""
    transaction_id: int = Field(..., description="ID da transação")
    proof_url: str = Field(..., description="URL do comprovante no GCS")
    status: str = Field(..., description="Novo status (waiting_approval)")
    message: str = Field(..., description="Mensagem de confirmação")
    
    class Config:
        schema_extra = {
            "example": {
                "transaction_id": 123,
                "proof_url": "https://storage.googleapis.com/eva-receipts/receipts/123/xxx.pdf",
                "status": "waiting_approval",
                "message": "Comprovante enviado com sucesso. Aguarde aprovação."
            }
        }


# ==========================================
# GENERIC
# ==========================================

class PaymentMethodInfo(BaseModel):
    """Informações sobre método de pagamento"""
    method: str = Field(..., description="Método (stripe, asaas, bitcoin, wise, nomad)")
    name: str = Field(..., description="Nome amigável")
    currencies: list[str] = Field(..., description="Moedas suportadas")
    processing_time: str = Field(..., description="Tempo de processamento")
    fees: str = Field(..., description="Taxas")
    available: bool = Field(..., description="Disponível")
    
    class Config:
        schema_extra = {
            "example": {
                "method": "stripe",
                "name": "Cartão de Crédito",
                "currencies": ["BRL", "USD", "EUR"],
                "processing_time": "Instantâneo",
                "fees": "4.99% + R$ 0.39",
                "available": True
            }
        }
