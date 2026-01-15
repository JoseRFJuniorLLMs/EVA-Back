"""
Wise Payment Service
Integração com Wise para pagamentos internacionais (Manual e Automatizado)
"""
from typing import Dict, Optional, List
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import logging
from datetime import datetime, timedelta

from database.payment_models import PaymentInstruction, WisePaymentReference, Transaction
from utils.wise_generator import WiseReferenceGenerator
from .wise_client import WiseAPIClient

logger = logging.getLogger(__name__)

class WisePaymentService:
    """Service para pagamentos via Wise/Nomad (transferência internacional)"""
    
    # Valores dos planos (mantidos do original)
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
        self.db = db
        self.client = WiseAPIClient() # Inicializa o cliente API
    
    async def get_payment_instructions(
        self,
        user_id: int,
        provider: str,
        currency: str,
        plan_tier: str,
        frequency: str
    ) -> Dict:
        """
        Retorna instruções de pagamento e gera Referência Única Rastreada.
        """
        # 1. Buscar instruções bancárias (conta destino)
        stmt = select(PaymentInstruction).where(
            PaymentInstruction.provider == provider,
            PaymentInstruction.currency == currency,
            PaymentInstruction.active == True
        )
        result = await self.db.execute(stmt)
        instruction = result.scalar_one_or_none()
        
        if not instruction:
            # Fallback para criar instrução se não existir seed
            raise ValueError(f"Instruções não encontradas para {provider}/{currency}")
        
        # 2. Obter valor do plano
        amount = self.PLAN_PRICES.get((plan_tier, frequency, currency))
        if not amount:
            raise ValueError(f"Plano inválido: {plan_tier}/{frequency}/{currency}")
        
        # 3. Gerar ou Recuperar Referência Única (Wise Payment Reference)
        if provider == 'wise':
            # Verificar se já existe uma referência pendente válida para este usuário/plano
            ref_stmt = select(WisePaymentReference).where(
                WisePaymentReference.user_id == user_id,
                WisePaymentReference.status == 'pending',
                WisePaymentReference.expected_amount == amount,
                WisePaymentReference.expected_currency == currency,
                WisePaymentReference.expires_at > datetime.utcnow()
            )
            ref_result = await self.db.execute(ref_stmt)
            existing_ref = ref_result.scalar_one_or_none()
            
            if existing_ref:
                reference_code = existing_ref.reference_code
                logger.info(f"Reusing existing reference {reference_code} for user {user_id}")
            else:
                # Gerar NOVA referência
                new_ref = WisePaymentReference.generate_for_user(user_id, float(amount), currency, plan_tier)
                self.db.add(new_ref)
                await self.db.commit()
                await self.db.refresh(new_ref)
                reference_code = new_ref.reference_code
                logger.info(f"Generated new reference {reference_code} for user {user_id}")
        else:
            # Nomad ou outro (sem automação completa ainda)
            import time
            reference_code = f"EVA-{user_id}-{int(time.time())}"
        
        # 4. Montar Resposta
        bank_details = instruction.details_json.copy() if instruction.details_json else {}
        
        # Remover template se existir
        if "reference_template" in bank_details:
            bank_details.pop("reference_template")
        
        # Atualizar instruções com a referência real
        instructions = bank_details.get("instructions", [])
        custom_instructions = [
            f"Transferir EXATAMENTE {currency} {amount}",
            f"Incluir OBRIGATORIAMENTE o código: {reference_code}",
            "O pagamento será identificado automaticamente em até 2 horas."
        ]
        
        return {
            "provider": provider,
            "currency": currency,
            "amount": amount,
            "reference_code": reference_code,
            "bank_details": bank_details,
            "instructions": custom_instructions
        }

    async def check_reference_status(self, reference_code: str) -> str:
        """Verifica status de uma referência (polling pelo frontend)"""
        stmt = select(WisePaymentReference).where(WisePaymentReference.reference_code == reference_code)
        result = await self.db.execute(stmt)
        ref = result.scalar_one_or_none()
        return ref.status if ref else "not_found"

    async def reconcile_transactions(self, profile_id: int):
        """
        Busca transações recentes na Wise e tenta casar com referências pendentes.
        (Backup para Webhooks)
        """
        accounts = await self.client.get_borderless_accounts(profile_id)
        
        for account in accounts:
            account_id = account['id']
            balances = account.get('balances', [])
            
            for balance in balances:
                currency = balance['currency']
                if currency not in ['USD', 'EUR', 'GBP']:
                    continue
                
                # Buscar extrato dos últimos 7 dias
                end = datetime.utcnow()
                start = end - timedelta(days=7)
                
                statement = await self.client.get_statement(
                    profile_id, account_id, currency, start, end
                )
                
                transactions = statement.get('transactions', [])
                for tx in transactions:
                    if tx['type'] == 'CREDIT': # Depósito
                        reference_text = tx.get('referenceNumber', '') or tx.get('details', {}).get('paymentReference', '')
                        amount = tx['amount']['value']
                        
                        await self.process_deposit(reference_text, float(amount), currency, tx['id'])

    async def process_deposit(self, reference_text: str, amount: float, currency: str, external_id: str) -> bool:
        """
        Processa um depósito identificado (via Webhook ou Polling).
        """
        # Tentar extrair ID ou usar referência completa
        # A referência pode vir "Ref: EVA-USER-123-ABCD" ou suja.
        # Vamos tentar encontrar o código EVA-USER no texto.
        
        import re
        match = re.search(r"EVA-USER-(\d+)-([A-F0-9]{4})", reference_text)
        
        if not match:
            logger.debug(f"No valid EVA reference found in: {reference_text}")
            return False
            
        full_ref = match.group(0) # EVA-USER-123-ABCD
        
        # Buscar no DB
        stmt = select(WisePaymentReference).where(
            WisePaymentReference.reference_code == full_ref,
            WisePaymentReference.status == 'pending'
        )
        result = await self.db.execute(stmt)
        ref = result.scalar_one_or_none()
        
        if not ref:
            logger.warning(f"Reference {full_ref} not found or not pending")
            return False
            
        # Validar Valor
        if abs(float(ref.expected_amount) - amount) > 0.50: # Tolerância pequena
            logger.error(f"Amount mismatch for {full_ref}: Expected {ref.expected_amount}, Got {amount}")
            # Pode marcar como 'partial_paid' ou alertar admin
            return False
            
        # SUCESSO!
        # Chamar WebhookService para ativar assinatura
        from services.webhook_service import WebhookService
        webhook_svc = WebhookService(self.db)
        
        # Criar Transação se não existir
        # Mas o WebhookService espera 'external_ref' que bata com TRANSACTION.
        # WisePaymentReference é o link.
        
        # Precisamos criar a Transaction primeiro
        new_transaction = Transaction(
            user_id=ref.user_id,
            amount=amount,
            currency=currency,
            provider='wise',
            status='pending', # Alterado para pending para o WebhookService ativar a assinatura
            external_ref=external_id, # ID da transação Wise
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(new_transaction)
        await self.db.commit() # Commit para gerar ID e salvar external_ref
        
        # Agora processar pagamento
        success = await webhook_svc.process_payment_confirmation(external_id, 'wise', amount)
        
        if success:
            ref.status = 'used'
            ref.used_at = datetime.utcnow()
            ref.subscription_id = new_transaction.subscription_id # WebhookService pode ter setado isso? Não, ele busca.
            await self.db.commit()
            logger.info(f"Successfully processed Wise deposit for {full_ref}")
            return True
            
        return False

    @staticmethod
    def get_plan_price(plan_tier: str, frequency: str, currency: str) -> Decimal:
        return WisePaymentService.PLAN_PRICES.get(
            (plan_tier, frequency, currency),
            Decimal("0.00")
        )
