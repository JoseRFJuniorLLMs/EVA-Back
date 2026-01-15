"""
Wise Payment Service
Integração com Wise para pagamentos internacionais
Retorna instruções bancárias estáticas do banco de dados
"""
from typing import Dict, Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)


class WisePaymentService:
    """Service para pagamentos via Wise/Nomad (transferência internacional)"""
    
    # Valores dos planos em diferentes moedas
    PLAN_PRICES = {
        ("gold", "monthly", "EUR"): Decimal("12.90"),
        ("gold", "yearly", "EUR"): Decimal("129.00"),
        ("diamond", "monthly", "EUR"): Decimal("19.90"),
        ("diamond", "yearly", "EUR"): Decimal("199.00"),
        
        ("gold", "monthly", "USD"): Decimal("14.90"),
        ("gold", "yearly", "USD"): Decimal("149.00"),
        ("diamond", "monthly", "USD"): Decimal("24.90"),
        ("diamond", "yearly", "USD"): Decimal("249.00"),
        
        ("gold", "monthly", "GBP"): Decimal("10.90"),
        ("gold", "yearly", "GBP"): Decimal("109.00"),
        ("diamond", "monthly", "GBP"): Decimal("17.90"),
        ("diamond", "yearly", "GBP"): Decimal("179.00"),
    }
    
    def __init__(self, db: AsyncSession):
        """
        Inicializa Wise service.
        
        Args:
            db: Sessão do banco de dados
        """
        self.db = db
    
    async def get_payment_instructions(
        self,
        user_id: int,
        provider: str,
        currency: str,
        plan_tier: str,
        frequency: str
    ) -> Dict:
        """
        Retorna instruções de pagamento para Wise/Nomad.
        
        Args:
            user_id: ID do usuário
            provider: Provider (wise ou nomad)
            currency: Moeda (EUR, USD, GBP)
            plan_tier: Plano (gold ou diamond)
            frequency: Frequência (monthly ou yearly)
        
        Returns:
            {
                "provider": "wise",
                "currency": "EUR",
                "amount": 12.90,
                "reference_code": "EVA-123-1705320000",
                "bank_details": {...},
                "instructions": [...]
            }
        
        Raises:
            ValueError: Se instruções não encontradas
        """
        # Importar model aqui para evitar circular import
        from database.models import PaymentInstruction
        
        # Buscar instruções no banco
        stmt = select(PaymentInstruction).where(
            PaymentInstruction.provider == provider,
            PaymentInstruction.currency == currency,
            PaymentInstruction.active == True
        )
        result = await self.db.execute(stmt)
        instruction = result.scalar_one_or_none()
        
        if not instruction:
            raise ValueError(f"Instruções não encontradas para {provider}/{currency}")
        
        # Obter valor do plano
        amount = self.PLAN_PRICES.get((plan_tier, frequency, currency))
        if not amount:
            raise ValueError(f"Plano inválido: {plan_tier}/{frequency}/{currency}")
        
        # Gerar código de referência único
        import time
        timestamp = int(time.time())
        reference_code = f"EVA-{user_id}-{timestamp}"
        
        # Extrair detalhes bancários
        bank_details = instruction.details_json.copy()
        
        # Substituir template de referência
        if "reference_template" in bank_details:
            bank_details.pop("reference_template")
        
        # Extrair instruções
        instructions = bank_details.pop("instructions", [
            f"Faça transferência para a conta acima",
            f"Use o código de referência: {reference_code}",
            f"Envie comprovante após transferência"
        ])
        
        logger.info(
            f"Payment instructions generated",
            extra={
                "user_id": user_id,
                "provider": provider,
                "currency": currency,
                "amount": float(amount)
            }
        )
        
        return {
            "provider": provider,
            "currency": currency,
            "amount": amount,
            "reference_code": reference_code,
            "bank_details": bank_details,
            "instructions": instructions
        }
    
    @staticmethod
    def get_plan_price(plan_tier: str, frequency: str, currency: str) -> Decimal:
        """
        Retorna preço do plano.
        
        Args:
            plan_tier: Plano (gold ou diamond)
            frequency: Frequência (monthly ou yearly)
            currency: Moeda (EUR, USD, GBP)
        
        Returns:
            Preço na moeda especificada
        """
        return WisePaymentService.PLAN_PRICES.get(
            (plan_tier, frequency, currency),
            Decimal("0.00")
        )
    
    @staticmethod
    def get_supported_currencies() -> list[str]:
        """Retorna moedas suportadas"""
        return ["EUR", "USD", "GBP"]
