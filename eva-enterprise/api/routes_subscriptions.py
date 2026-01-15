"""
Rotas de Subscriptions
Endpoints para gerenciar assinaturas do usuário
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
import logging
from datetime import datetime

from database.connection import get_db
from schemas.subscription import (
    SubscriptionResponse,
    SubscriptionCancelRequest,
    SubscriptionHistoryItem
)
from schemas.transaction import TransactionResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


# ==========================================
# MINHA ASSINATURA
# ==========================================

@router.get("/me", response_model=SubscriptionResponse)
async def get_my_subscription(
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna assinatura ativa do usuário autenticado.
    
    **Retorna:**
    - Plano atual (basic, gold, diamond)
    - Status (active, past_due, canceled)
    - Período atual
    - Dias restantes
    - Método de pagamento padrão
    
    **Rate Limit:** 20/minuto
    """
    # TODO: Obter user_id do token JWT
    user_id = 1  # Placeholder
    
    try:
        # Importar model aqui para evitar circular import
        from database.models import Subscription
        
        # Buscar assinatura ativa
        stmt = select(Subscription).where(
            and_(
                Subscription.user_id == user_id,
                Subscription.status.in_(["active", "trialing", "past_due"])
            )
        ).order_by(Subscription.created_at.desc())
        
        result = await db.execute(stmt)
        subscription = result.scalar_one_or_none()
        
        if not subscription:
            raise HTTPException(404, detail="Nenhuma assinatura encontrada")
        
        # Calcular dias restantes
        days_remaining = (subscription.current_period_end - datetime.utcnow()).total_seconds() / 86400
        
        return SubscriptionResponse(
            id=subscription.id,
            user_id=subscription.user_id,
            plan_tier=subscription.plan_tier,
            status=subscription.status,
            current_period_start=subscription.current_period_start,
            current_period_end=subscription.current_period_end,
            payment_method_default=subscription.payment_method_default,
            days_remaining=days_remaining,
            created_at=subscription.created_at,
            updated_at=subscription.updated_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching subscription: {e}", extra={"user_id": user_id})
        raise HTTPException(500, detail="Erro ao buscar assinatura")


# ==========================================
# CANCELAR ASSINATURA
# ==========================================

@router.post("/cancel")
async def cancel_subscription(
    data: SubscriptionCancelRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Cancela assinatura do usuário.
    
    **Opções:**
    - `immediate=false`: Cancela no fim do período (padrão)
    - `immediate=true`: Cancela imediatamente
    
    **Fluxo:**
    1. Se Stripe: cancela no gateway
    2. Atualiza status no DB
    3. Envia email de confirmação
    
    **Rate Limit:** 5/minuto
    """
    # TODO: Obter user_id do token JWT
    user_id = 1  # Placeholder
    
    try:
        from database.models import Subscription
        
        # Buscar assinatura ativa
        stmt = select(Subscription).where(
            and_(
                Subscription.user_id == user_id,
                Subscription.status == "active"
            )
        )
        
        result = await db.execute(stmt)
        subscription = result.scalar_one_or_none()
        
        if not subscription:
            raise HTTPException(404, detail="Nenhuma assinatura ativa encontrada")
        
        # Se tem external_subscription_id (Stripe), cancelar no gateway
        if subscription.external_subscription_id:
            from services.payment import StripePaymentService
            stripe_service = StripePaymentService()
            
            await stripe_service.cancel_subscription(
                subscription.external_subscription_id
            )
        
        # Atualizar status
        if data.immediate:
            subscription.status = "canceled"
            subscription.current_period_end = datetime.utcnow()
        else:
            # Cancelar no fim do período
            subscription.status = "active"  # Mantém ativo até expirar
            # TODO: Adicionar flag cancel_at_period_end
        
        await db.commit()
        
        logger.info(
            f"Subscription canceled",
            extra={
                "user_id": user_id,
                "subscription_id": subscription.id,
                "immediate": data.immediate
            }
        )
        
        return {
            "message": "Assinatura cancelada com sucesso",
            "canceled_at": datetime.utcnow().isoformat(),
            "access_until": subscription.current_period_end.isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error canceling subscription: {e}", extra={"user_id": user_id})
        raise HTTPException(500, detail="Erro ao cancelar assinatura")


# ==========================================
# HISTÓRICO DE ASSINATURAS
# ==========================================

@router.get("/history", response_model=List[SubscriptionHistoryItem])
async def get_subscription_history(
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna histórico de todas as assinaturas do usuário.
    
    **Inclui:**
    - Assinaturas antigas (canceladas)
    - Total pago por período
    - Número de transações
    
    **Rate Limit:** 20/minuto
    """
    # TODO: Obter user_id do token JWT
    user_id = 1  # Placeholder
    
    try:
        from database.models import Subscription, Transaction
        from sqlalchemy import func
        
        # Buscar todas as assinaturas do usuário
        stmt = select(
            Subscription,
            func.sum(Transaction.amount).label("total_paid"),
            func.count(Transaction.id).label("transactions_count")
        ).outerjoin(
            Transaction,
            Transaction.subscription_id == Subscription.id
        ).where(
            Subscription.user_id == user_id
        ).group_by(
            Subscription.id
        ).order_by(
            Subscription.created_at.desc()
        )
        
        result = await db.execute(stmt)
        rows = result.all()
        
        history = []
        for row in rows:
            subscription = row[0]
            total_paid = row[1] or 0
            transactions_count = row[2] or 0
            
            history.append(SubscriptionHistoryItem(
                id=subscription.id,
                plan_tier=subscription.plan_tier,
                status=subscription.status,
                started_at=subscription.current_period_start,
                ended_at=subscription.current_period_end if subscription.status == "canceled" else None,
                total_paid=total_paid,
                transactions_count=transactions_count
            ))
        
        return history
    
    except Exception as e:
        logger.error(f"Error fetching history: {e}", extra={"user_id": user_id})
        raise HTTPException(500, detail="Erro ao buscar histórico")


# ==========================================
# TRANSAÇÕES DA ASSINATURA
# ==========================================

@router.get("/{subscription_id}/transactions", response_model=List[TransactionResponse])
async def get_subscription_transactions(
    subscription_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna todas as transações de uma assinatura.
    
    **Útil para:**
    - Ver histórico de pagamentos
    - Baixar comprovantes
    - Verificar falhas
    
    **Rate Limit:** 20/minuto
    """
    # TODO: Obter user_id do token JWT e verificar ownership
    user_id = 1  # Placeholder
    
    try:
        from database.models import Transaction
        
        stmt = select(Transaction).where(
            Transaction.subscription_id == subscription_id
        ).order_by(
            Transaction.created_at.desc()
        )
        
        result = await db.execute(stmt)
        transactions = result.scalars().all()
        
        return [
            TransactionResponse(
                id=t.id,
                user_id=t.user_id,
                subscription_id=t.subscription_id,
                amount=t.amount,
                currency=t.currency,
                provider=t.provider,
                status=t.status,
                external_ref=t.external_ref,
                proof_url=t.proof_url,
                failure_reason=t.failure_reason,
                created_at=t.created_at,
                updated_at=t.updated_at
            )
            for t in transactions
        ]
    
    except Exception as e:
        logger.error(f"Error fetching transactions: {e}")
        raise HTTPException(500, detail="Erro ao buscar transações")
