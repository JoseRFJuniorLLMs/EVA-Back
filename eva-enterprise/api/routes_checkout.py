"""
Rotas de Checkout
Endpoints para criação de sessões de pagamento
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import os
import logging

from database.connection import get_db
from schemas.checkout import (
    StripeCheckoutRequest,
    StripeCheckoutResponse,
    AsaasPixRequest,
    AsaasPixResponse,
    BitcoinInvoiceRequest,
    BitcoinInvoiceResponse,
    InternationalInstructionsRequest,
    InternationalInstructionsResponse,
    ReceiptUploadResponse
)
from services.payment import (
    StripePaymentService,
    AsaasPaymentService,
    OpenNodePaymentService,
    WisePaymentService
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/checkout", tags=["Checkout"])


# ==========================================
# STRIPE (CARTÃO DE CRÉDITO)
# ==========================================

@router.post("/stripe-session", response_model=StripeCheckoutResponse, status_code=201)
async def create_stripe_checkout(
    data: StripeCheckoutRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Cria sessão de checkout Stripe para cartão de crédito.
    
    **Planos disponíveis:**
    - Gold: R$ 59,90/mês ou R$ 599/ano
    - Diamond: R$ 99,90/mês ou R$ 999/ano
    
    **Fluxo:**
    1. Cria sessão no Stripe
    2. Retorna URL para redirect
    3. Usuário completa pagamento no Stripe
    4. Webhook confirma pagamento
    
    **Rate Limit:** 5/minuto
    """
    # TODO: Obter user_id do token JWT
    user_id = 1  # Placeholder
    
    # URLs de sucesso/cancelamento
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    success_url = data.success_url or f"{frontend_url}/payment/success"
    cancel_url = data.cancel_url or f"{frontend_url}/payment/cancel"
    
    try:
        stripe_service = StripePaymentService()
        
        result = await stripe_service.create_checkout_session(
            user_id=user_id,
            plan_tier=data.plan_tier,
            frequency=data.frequency,
            success_url=success_url,
            cancel_url=cancel_url
        )
        
        return StripeCheckoutResponse(**result)
    
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    except Exception as e:
        logger.error(f"Stripe checkout error: {e}", extra={"user_id": user_id})
        raise HTTPException(500, detail="Erro ao criar sessão de checkout")


# ==========================================
# ASAAS (PIX)
# ==========================================

@router.post("/asaas-pix", response_model=AsaasPixResponse, status_code=201)
async def create_asaas_pix(
    data: AsaasPixRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Cria cobrança Pix via Asaas.
    
    **Retorna:**
    - QR Code (imagem)
    - Código Pix copia e cola
    - Validade: 24 horas
    
    **Fluxo:**
    1. Gera QR Code Pix
    2. Usuário paga via app bancário
    3. Webhook confirma pagamento (instantâneo)
    
    **Rate Limit:** 10/minuto
    """
    # TODO: Obter user_id do token JWT
    user_id = 1  # Placeholder
    
    try:
        asaas_service = AsaasPaymentService()
        
        result = await asaas_service.create_pix_charge(
            user_id=user_id,
            plan_tier=data.plan_tier,
            frequency=data.frequency
        )
        
        return AsaasPixResponse(**result)
    
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    except Exception as e:
        logger.error(f"Asaas Pix error: {e}", extra={"user_id": user_id})
        raise HTTPException(500, detail="Erro ao gerar QR Code Pix")


# ==========================================
# OPENNODE (BITCOIN LIGHTNING)
# ==========================================

@router.post("/bitcoin", response_model=BitcoinInvoiceResponse, status_code=201)
async def create_bitcoin_invoice(
    data: BitcoinInvoiceRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Cria invoice Bitcoin Lightning Network.
    
    **Retorna:**
    - Invoice Lightning (lnbc...)
    - QR Code
    - Conversão BRL → BTC automática
    - Validade: 15 minutos
    
    **Fluxo:**
    1. Converte BRL para BTC (cotação Coingecko + 5% buffer)
    2. Gera invoice Lightning
    3. Usuário paga via carteira Lightning
    4. Webhook confirma (instantâneo)
    
    **Rate Limit:** 5/minuto
    """
    # TODO: Obter user_id do token JWT
    user_id = 1  # Placeholder
    
    api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    try:
        opennode_service = OpenNodePaymentService()
        
        result = await opennode_service.create_lightning_invoice(
            user_id=user_id,
            plan_tier=data.plan_tier,
            frequency=data.frequency,
            callback_url=f"{api_base_url}/api/v1/webhooks/opennode",
            success_url=f"{frontend_url}/payment/success"
        )
        
        return BitcoinInvoiceResponse(**result)
    
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    except Exception as e:
        logger.error(f"Bitcoin invoice error: {e}", extra={"user_id": user_id})
        raise HTTPException(500, detail="Erro ao criar invoice Bitcoin")


# ==========================================
# WISE/NOMAD (INTERNACIONAL)
# ==========================================

@router.post("/instructions", response_model=InternationalInstructionsResponse)
async def get_payment_instructions(
    data: InternationalInstructionsRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna instruções bancárias para transferência internacional.
    
    **Providers:**
    - Wise: EUR, USD, GBP
    - Nomad: USD, EUR
    
    **Retorna:**
    - Dados bancários (IBAN, SWIFT, etc)
    - Código de referência ÚNICO
    - Instruções passo a passo
    
    **Fluxo:**
    1. Usuário recebe instruções
    2. Faz transferência no banco
    3. Envia comprovante via `/upload-receipt`
    4. Admin aprova manualmente
    
    **Rate Limit:** 20/minuto
    """
    # TODO: Obter user_id do token JWT
    user_id = 1  # Placeholder
    
    try:
        wise_service = WisePaymentService(db)
        
        result = await wise_service.get_payment_instructions(
            user_id=user_id,
            provider=data.provider,
            currency=data.currency,
            plan_tier=data.plan_tier,
            frequency=data.frequency
        )
        
        return InternationalInstructionsResponse(**result)
    
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    except Exception as e:
        logger.error(f"Payment instructions error: {e}", extra={"user_id": user_id})
        raise HTTPException(500, detail="Erro ao obter instruções de pagamento")


# ==========================================
# UPLOAD DE COMPROVANTE
# ==========================================

@router.post("/upload-receipt", response_model=ReceiptUploadResponse)
async def upload_payment_receipt(
    transaction_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload de comprovante de pagamento (Wise/Nomad).
    
    **Validações:**
    - Tipos aceitos: JPEG, PNG, PDF
    - Tamanho máximo: 5MB
    - Transação deve existir e pertencer ao usuário
    
    **Fluxo:**
    1. Upload para Google Cloud Storage
    2. Atualiza transaction.proof_url
    3. Muda status para 'waiting_approval'
    4. Notifica admin
    
    **Rate Limit:** 10/minuto
    """
    # TODO: Obter user_id do token JWT
    user_id = 1  # Placeholder
    
    # Validar tipo de arquivo
    allowed_types = ["image/jpeg", "image/png", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            400,
            detail=f"Tipo de arquivo inválido. Aceitos: {', '.join(allowed_types)}"
        )
    
    # Validar tamanho
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:  # 5MB
        raise HTTPException(400, detail="Arquivo muito grande (máximo 5MB)")
    
    # TODO: Implementar upload para GCS
    # TODO: Atualizar transaction no banco
    # TODO: Enviar notificação para admin
    
    raise HTTPException(501, detail="Upload de comprovante não implementado ainda")
