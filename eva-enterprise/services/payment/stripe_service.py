"""
Stripe Payment Service
Integração com Stripe para pagamentos com cartão de crédito
"""
import stripe
from typing import Dict, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import os
import logging

logger = logging.getLogger(__name__)


class StripePaymentService:
    """Service para integração com Stripe"""
    
    # Mapeamento de planos para Price IDs do Stripe
    PRICE_MAP = {
        ("gold", "monthly"): os.getenv("STRIPE_PRICE_GOLD_MONTHLY", "price_gold_monthly"),
        ("gold", "yearly"): os.getenv("STRIPE_PRICE_GOLD_YEARLY", "price_gold_yearly"),
        ("diamond", "monthly"): os.getenv("STRIPE_PRICE_DIAMOND_MONTHLY", "price_diamond_monthly"),
        ("diamond", "yearly"): os.getenv("STRIPE_PRICE_DIAMOND_YEARLY", "price_diamond_yearly"),
    }
    
    # Valores dos planos (para referência)
    PLAN_PRICES = {
        ("gold", "monthly"): Decimal("59.90"),
        ("gold", "yearly"): Decimal("599.00"),
        ("diamond", "monthly"): Decimal("99.90"),
        ("diamond", "yearly"): Decimal("999.00"),
    }
    
    def __init__(self):
        """Inicializa Stripe com API key"""
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
        stripe.api_version = "2024-11-20.acacia"  # Versão fixa
        
        if not stripe.api_key:
            raise ValueError("STRIPE_SECRET_KEY não configurada")
    
    async def create_checkout_session(
        self,
        user_id: int,
        plan_tier: str,
        frequency: str,
        success_url: str,
        cancel_url: str,
        customer_email: Optional[str] = None
    ) -> Dict:
        """
        Cria sessão de checkout do Stripe.
        
        Args:
            user_id: ID do usuário
            plan_tier: Plano (gold ou diamond)
            frequency: Frequência (monthly ou yearly)
            success_url: URL de sucesso
            cancel_url: URL de cancelamento
            customer_email: Email do cliente (opcional)
        
        Returns:
            {
                "url": "https://checkout.stripe.com/...",
                "session_id": "cs_test_...",
                "expires_at": 1705320000
            }
        
        Raises:
            ValueError: Se plano inválido
            stripe.error.StripeError: Erros da API Stripe
        """
        # Validar plano
        price_id = self.PRICE_MAP.get((plan_tier, frequency))
        if not price_id:
            raise ValueError(f"Plano inválido: {plan_tier}/{frequency}")
        
        try:
            # Criar sessão de checkout
            session = stripe.checkout.Session.create(
                mode="subscription",
                line_items=[{
                    "price": price_id,
                    "quantity": 1,
                }],
                success_url=f"{success_url}?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=cancel_url,
                client_reference_id=str(user_id),
                customer_email=customer_email,
                metadata={
                    "user_id": str(user_id),
                    "plan_tier": plan_tier,
                    "frequency": frequency,
                    "created_by": "eva_api"
                },
                subscription_data={
                    "metadata": {
                        "user_id": str(user_id),
                        "plan_tier": plan_tier
                    }
                },
                expires_at=int((datetime.utcnow() + timedelta(hours=1)).timestamp()),
                automatic_tax={"enabled": False},  # Configurar se necessário
                billing_address_collection="required",
                allow_promotion_codes=True,  # Permitir cupons
            )
            
            logger.info(
                f"Stripe checkout session created",
                extra={
                    "user_id": user_id,
                    "session_id": session.id,
                    "plan_tier": plan_tier,
                    "frequency": frequency
                }
            )
            
            return {
                "url": session.url,
                "session_id": session.id,
                "expires_at": session.expires_at
            }
        
        except stripe.error.StripeError as e:
            logger.error(
                f"Stripe error: {e}",
                extra={"user_id": user_id, "error": str(e)}
            )
            raise
    
    async def get_session(self, session_id: str) -> Dict:
        """
        Busca sessão de checkout pelo ID.
        
        Args:
            session_id: ID da sessão
        
        Returns:
            Dados da sessão
        """
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return {
                "id": session.id,
                "status": session.status,
                "payment_status": session.payment_status,
                "amount_total": session.amount_total / 100 if session.amount_total else 0,
                "currency": session.currency,
                "customer": session.customer,
                "subscription": session.subscription,
                "metadata": session.metadata
            }
        except stripe.error.StripeError as e:
            logger.error(f"Error retrieving session: {e}")
            raise
    
    async def cancel_subscription(self, subscription_id: str) -> Dict:
        """
        Cancela assinatura no Stripe.
        
        Args:
            subscription_id: ID da assinatura no Stripe
        
        Returns:
            Dados da assinatura cancelada
        """
        try:
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
            
            logger.info(
                f"Stripe subscription canceled",
                extra={"subscription_id": subscription_id}
            )
            
            return {
                "id": subscription.id,
                "status": subscription.status,
                "cancel_at": subscription.cancel_at,
                "cancel_at_period_end": subscription.cancel_at_period_end
            }
        except stripe.error.StripeError as e:
            logger.error(f"Error canceling subscription: {e}")
            raise
    
    async def get_customer(self, customer_id: str) -> Dict:
        """
        Busca dados do cliente no Stripe.
        
        Args:
            customer_id: ID do cliente
        
        Returns:
            Dados do cliente
        """
        try:
            customer = stripe.Customer.retrieve(customer_id)
            return {
                "id": customer.id,
                "email": customer.email,
                "name": customer.name,
                "metadata": customer.metadata
            }
        except stripe.error.StripeError as e:
            logger.error(f"Error retrieving customer: {e}")
            raise
    
    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
        webhook_secret: str
    ) -> Dict:
        """
        Verifica assinatura de webhook do Stripe.
        
        Args:
            payload: Body da request (bytes)
            signature: Header Stripe-Signature
            webhook_secret: Secret do webhook
        
        Returns:
            Evento verificado
        
        Raises:
            ValueError: Payload inválido
            stripe.error.SignatureVerificationError: Assinatura inválida
        """
        try:
            event = stripe.Webhook.construct_event(
                payload,
                signature,
                webhook_secret
            )
            return event
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            raise
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {e}")
            raise
    
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
        return StripePaymentService.PLAN_PRICES.get(
            (plan_tier, frequency),
            Decimal("0.00")
        )
