from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timedelta
import logging

from database.payment_models import Transaction, Subscription
from database.models import Usuario as User

logger = logging.getLogger(__name__)

class WebhookService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_payment_confirmation(self, external_ref: str, provider: str, amount: float = None) -> bool:
        """
        Processa confirmação de pagamento:
        1. Localiza transação
        2. Marca como paga
        3. Ativa/Renova assinatura
        4. Atualiza tier do usuário
        """
        try:
            # 1. Buscar transação
            stmt = select(Transaction).where(Transaction.external_ref == external_ref)
            result = await self.db.execute(stmt)
            transaction = result.scalar_one_or_none()

            if not transaction:
                logger.error(f"Transaction not found for ref: {external_ref}")
                return False
            
            if transaction.status == 'paid':
                logger.info(f"Transaction {external_ref} already paid")
                return True

            # 2. Atualizar Transação
            transaction.status = 'paid'
            transaction.updated_at = datetime.utcnow()
            if amount:
                # Validar valor se necessário
                pass

            # 3. Buscar Assinatura
            sub_stmt = select(Subscription).where(Subscription.id == transaction.subscription_id)
            sub_result = await self.db.execute(sub_stmt)
            subscription = sub_result.scalar_one_or_none()
            
            if not subscription:
                logger.error("Subscription not found for transaction")
                return False

            # 4. Atualizar Assinatura (Renovação)
            # Definir novo período. Se mensal +30 dias, anual +365
            frequency = subscription.metadata_json.get('frequency', 'monthly')
            days_to_add = 365 if frequency == 'yearly' else 30
            
            now = datetime.utcnow()
            # Se já venceu, começa de agora. Se não, soma ao final atual
            start_date = now if not subscription.current_period_end or subscription.current_period_end < now else subscription.current_period_end
            new_end_date = start_date + timedelta(days=days_to_add)

            subscription.status = 'active'
            subscription.current_period_end = new_end_date
            subscription.updated_at = now

            # 5. Atualizar Usuário (Tier)
            user_stmt = select(User).where(User.id == getattr(subscription, 'user_id', transaction.user_id))
            user_result = await self.db.execute(user_stmt)
            user = user_result.scalar_one_or_none()

            if user:
                user.subscription_tier = subscription.plan_tier
                # user.tipo = 'assinante' # Opcional se usar role
            
            await self.db.commit()
            
            logger.info(f"Payment processed successfully. User {user.id} is now {subscription.plan_tier}")
            return True

        except Exception as e:
            logger.error(f"Error processing payment confirmation: {e}")
            await self.db.rollback()
            return False

    async def process_payment_failure(self, external_ref: str, reason: str = None):
        """Marca transação como falha e notifica"""
        stmt = select(Transaction).where(Transaction.external_ref == external_ref)
        result = await self.db.execute(stmt)
        transaction = result.scalar_one_or_none()

        if transaction:
            transaction.status = 'failed'
            transaction.failure_reason = reason
            transaction.updated_at = datetime.utcnow()
            await self.db.commit()
            logger.warning(f"Transaction {external_ref} marked as failed")
