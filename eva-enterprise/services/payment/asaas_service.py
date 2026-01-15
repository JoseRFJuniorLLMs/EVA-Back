"""
Asaas Payment Service
Integração com Asaas para pagamentos via Pix
"""
import httpx
from typing import Dict, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import os
import logging
import hmac
import hashlib

logger = logging.getLogger(__name__)


class AsaasPaymentService:
    """Service para integração com Asaas (Pix)"""
    
    BASE_URL = "https://api.asaas.com/v3"
    
    # Valores dos planos
    PLAN_PRICES = {
        ("gold", "monthly"): Decimal("59.90"),
        ("gold", "yearly"): Decimal("599.00"),
        ("diamond", "monthly"): Decimal("99.90"),
        ("diamond", "yearly"): Decimal("999.00"),
    }
    
    def __init__(self):
        """Inicializa Asaas com API key"""
        self.api_key = os.getenv("ASAAS_API_KEY")
        self.webhook_token = os.getenv("ASAAS_WEBHOOK_TOKEN")
        
        if not self.api_key:
            raise ValueError("ASAAS_API_KEY não configurada")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def create_pix_charge(
        self,
        user_id: int,
        plan_tier: str,
        frequency: str,
        customer_name: Optional[str] = None,
        customer_cpf: Optional[str] = None
    ) -> Dict:
        """
        Cria cobrança Pix no Asaas.
        
        Args:
            user_id: ID do usuário
            plan_tier: Plano (gold ou diamond)
            frequency: Frequência (monthly ou yearly)
            customer_name: Nome do cliente (opcional)
            customer_cpf: CPF do cliente (opcional)
        
        Returns:
            {
                "charge_id": "pay_xxx",
                "qr_code_url": "https://...",
                "qr_code_payload": "00020126...",
                "amount": 59.90,
                "expires_at": "2026-01-16T12:00:00Z"
            }
        
        Raises:
            ValueError: Se plano inválido
            httpx.HTTPError: Erros da API Asaas
        """
        # Obter valor do plano
        amount = self.PLAN_PRICES.get((plan_tier, frequency))
        if not amount:
            raise ValueError(f"Plano inválido: {plan_tier}/{frequency}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # 1. Criar/buscar customer
                customer_data = {
                    "name": customer_name or f"User {user_id}",
                    "cpfCnpj": customer_cpf or "00000000000",  # CPF fake para dev
                    "externalReference": str(user_id)
                }
                
                customer_response = await client.post(
                    f"{self.BASE_URL}/customers",
                    headers=self.headers,
                    json=customer_data
                )
                customer_response.raise_for_status()
                customer = customer_response.json()
                
                # 2. Criar cobrança Pix
                due_date = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
                external_ref = f"user_{user_id}_{int(datetime.utcnow().timestamp())}"
                
                charge_data = {
                    "customer": customer["id"],
                    "billingType": "PIX",
                    "value": float(amount),
                    "dueDate": due_date,
                    "description": f"EVA {plan_tier.title()} - Assinatura {frequency}",
                    "externalReference": external_ref,
                    "postalService": False
                }
                
                charge_response = await client.post(
                    f"{self.BASE_URL}/payments",
                    headers=self.headers,
                    json=charge_data
                )
                charge_response.raise_for_status()
                charge = charge_response.json()
                
                # 3. Obter QR Code Pix
                qr_response = await client.get(
                    f"{self.BASE_URL}/payments/{charge['id']}/pixQrCode",
                    headers=self.headers
                )
                qr_response.raise_for_status()
                qr_data = qr_response.json()
                
                logger.info(
                    f"Asaas Pix charge created",
                    extra={
                        "user_id": user_id,
                        "charge_id": charge["id"],
                        "amount": float(amount)
                    }
                )
                
                return {
                    "charge_id": charge["id"],
                    "qr_code_url": qr_data.get("encodedImage"),  # Base64 ou URL
                    "qr_code_payload": qr_data["payload"],  # Copia e cola
                    "amount": amount,
                    "expires_at": qr_data.get("expirationDate", due_date),
                    "external_ref": external_ref
                }
            
            except httpx.HTTPError as e:
                logger.error(
                    f"Asaas API error: {e}",
                    extra={"user_id": user_id, "error": str(e)}
                )
                raise
    
    async def get_payment_status(self, charge_id: str) -> Dict:
        """
        Verifica status de pagamento.
        
        Args:
            charge_id: ID da cobrança
        
        Returns:
            Status do pagamento
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/payments/{charge_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                payment = response.json()
                
                return {
                    "id": payment["id"],
                    "status": payment["status"],
                    "value": payment["value"],
                    "external_reference": payment.get("externalReference"),
                    "payment_date": payment.get("paymentDate")
                }
            
            except httpx.HTTPError as e:
                logger.error(f"Error getting payment status: {e}")
                raise
    
    def verify_webhook_token(self, token: str) -> bool:
        """
        Verifica token do webhook Asaas.
        
        Args:
            token: Token recebido no webhook
        
        Returns:
            True se válido
        """
        if not self.webhook_token:
            logger.warning("ASAAS_WEBHOOK_TOKEN não configurado")
            return True  # Permitir em dev
        
        return token == self.webhook_token
    
    @staticmethod
    def get_plan_price(plan_tier: str, frequency: str) -> Decimal:
        """
        Retorna preço do plano.
        
        Args:
            plan_tier: Plano (gold ou diamond)
            frequency: Frequência (monthly ou yearly)
        
        Returns:
            Preço em BRL
        """
        return AsaasPaymentService.PLAN_PRICES.get(
            (plan_tier, frequency),
            Decimal("0.00")
        )
