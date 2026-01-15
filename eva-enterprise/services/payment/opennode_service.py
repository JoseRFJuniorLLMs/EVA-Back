"""
OpenNode Payment Service
Integração com OpenNode para pagamentos via Bitcoin Lightning Network
"""
import httpx
from typing import Dict
from datetime import datetime
from decimal import Decimal
import os
import logging
import hmac
import hashlib

logger = logging.getLogger(__name__)


class OpenNodePaymentService:
    """Service para integração com OpenNode (Bitcoin Lightning)"""
    
    BASE_URL = "https://api.opennode.com/v1"
    COINGECKO_URL = "https://api.coingecko.com/api/v3"
    
    # Valores dos planos em BRL
    PLAN_PRICES_BRL = {
        ("gold", "monthly"): Decimal("59.90"),
        ("gold", "yearly"): Decimal("599.00"),
        ("diamond", "monthly"): Decimal("99.90"),
        ("diamond", "yearly"): Decimal("999.00"),
    }
    
    def __init__(self):
        """Inicializa OpenNode com API key"""
        self.api_key = os.getenv("OPENNODE_API_KEY")
        self.webhook_secret = os.getenv("OPENNODE_WEBHOOK_SECRET")
        
        if not self.api_key:
            raise ValueError("OPENNODE_API_KEY não configurada")
        
        self.headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }
    
    async def get_btc_price_brl(self) -> Decimal:
        """
        Obtém cotação BTC/BRL via Coingecko.
        
        Returns:
            Preço do BTC em BRL
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(
                    f"{self.COINGECKO_URL}/simple/price",
                    params={"ids": "bitcoin", "vs_currencies": "brl"}
                )
                response.raise_for_status()
                data = response.json()
                
                btc_price = Decimal(str(data["bitcoin"]["brl"]))
                logger.info(f"BTC price: R$ {btc_price}")
                
                return btc_price
            
            except httpx.HTTPError as e:
                logger.error(f"Error fetching BTC price: {e}")
                # Fallback: preço aproximado
                return Decimal("400000.00")
    
    async def create_lightning_invoice(
        self,
        user_id: int,
        plan_tier: str,
        frequency: str,
        callback_url: str,
        success_url: str
    ) -> Dict:
        """
        Cria invoice Lightning Network.
        
        Args:
            user_id: ID do usuário
            plan_tier: Plano (gold ou diamond)
            frequency: Frequência (monthly ou yearly)
            callback_url: URL para webhook
            success_url: URL de sucesso
        
        Returns:
            {
                "invoice_id": "abc123",
                "lightning_invoice": "lnbc...",
                "qr_code_url": "https://...",
                "amount_btc": 0.00015,
                "amount_brl": 59.90,
                "expires_at": "2026-01-15T13:15:00Z"
            }
        
        Raises:
            ValueError: Se plano inválido
            httpx.HTTPError: Erros da API OpenNode
        """
        # Obter valor em BRL
        amount_brl = self.PLAN_PRICES_BRL.get((plan_tier, frequency))
        if not amount_brl:
            raise ValueError(f"Plano inválido: {plan_tier}/{frequency}")
        
        # Obter cotação BTC
        btc_price_brl = await self.get_btc_price_brl()
        
        # Calcular BTC com 5% de buffer para volatilidade
        amount_btc = (amount_brl / btc_price_brl) * Decimal("1.05")
        amount_satoshis = int(amount_btc * 100_000_000)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                order_id = f"user_{user_id}_{int(datetime.utcnow().timestamp())}"
                
                invoice_data = {
                    "amount": amount_satoshis,
                    "currency": "btc",
                    "description": f"EVA {plan_tier.title()} Subscription",
                    "callback_url": callback_url,
                    "success_url": success_url,
                    "customer_email": f"user{user_id}@eva.com",
                    "order_id": order_id,
                    "ttl": 900  # 15 minutos
                }
                
                response = await client.post(
                    f"{self.BASE_URL}/charges",
                    headers=self.headers,
                    json=invoice_data
                )
                response.raise_for_status()
                result = response.json()
                invoice = result["data"]
                
                # Gerar QR Code URL
                lightning_invoice = invoice["lightning_invoice"]["payreq"]
                qr_code_url = f"https://chart.googleapis.com/chart?chs=300x300&cht=qr&chl={lightning_invoice}"
                
                logger.info(
                    f"Lightning invoice created",
                    extra={
                        "user_id": user_id,
                        "invoice_id": invoice["id"],
                        "amount_satoshis": amount_satoshis
                    }
                )
                
                return {
                    "invoice_id": invoice["id"],
                    "lightning_invoice": lightning_invoice,
                    "qr_code_url": qr_code_url,
                    "amount_btc": float(amount_btc),
                    "amount_brl": float(amount_brl),
                    "expires_at": invoice.get("expires_at", ""),
                    "order_id": order_id
                }
            
            except httpx.HTTPError as e:
                logger.error(
                    f"OpenNode API error: {e}",
                    extra={"user_id": user_id, "error": str(e)}
                )
                raise
    
    async def get_invoice_status(self, invoice_id: str) -> Dict:
        """
        Verifica status de invoice.
        
        Args:
            invoice_id: ID do invoice
        
        Returns:
            Status do invoice
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/charge/{invoice_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                result = response.json()
                invoice = result["data"]
                
                return {
                    "id": invoice["id"],
                    "status": invoice["status"],
                    "order_id": invoice.get("order_id"),
                    "amount": invoice.get("amount")
                }
            
            except httpx.HTTPError as e:
                logger.error(f"Error getting invoice status: {e}")
                raise
    
    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str
    ) -> bool:
        """
        Verifica assinatura de webhook OpenNode.
        
        Args:
            payload: Body da request (bytes)
            signature: Signature do header
        
        Returns:
            True se válido
        """
        if not self.webhook_secret:
            logger.warning("OPENNODE_WEBHOOK_SECRET não configurado")
            return True  # Permitir em dev
        
        expected = hmac.new(
            key=self.webhook_secret.encode(),
            msg=payload,
            digestmod=hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected, signature)
