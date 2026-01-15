"""
Rotas Admin de Pagamentos
Endpoints para administração de pagamentos e aprovações
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Optional
import logging
from datetime import datetime

from database.connection import get_db
from schemas.transaction import TransactionResponse, TransactionListResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/payments", tags=["Admin - Payments"])


# ==========================================
# COMPROVANTES PENDENTES
# ==========================================

@router.get("/pending-receipts", response_model=TransactionListResponse)
async def get_pending_receipts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista comprovantes pendentes de aprovação (Wise/Nomad).
    
    **Requer:** Admin role
    
    **Retorna:**
    - Transações com status 'waiting_approval'
    - URL do comprovante
    - Tempo de espera
    - Paginação
    
    **Rate Limit:** 50/minuto
    """
    # TODO: Verificar se usuário é admin
    
    try:
        from database.models import Transaction, Usuario
        
        # Count total
        count_stmt = select(func.count(Transaction.id)).where(
            Transaction.status == "waiting_approval"
        )
        total_result = await db.execute(count_stmt)
        total = total_result.scalar()
        
        # Buscar transações
        offset = (page - 1) * page_size
        stmt = select(Transaction).where(
            Transaction.status == "waiting_approval"
        ).order_by(
            Transaction.created_at.asc()
        ).offset(offset).limit(page_size)
        
        result = await db.execute(stmt)
        transactions = result.scalars().all()
        
        return TransactionListResponse(
            transactions=[
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
            ],
            total=total,
            page=page,
            page_size=page_size
        )
    
    except Exception as e:
        logger.error(f"Error fetching pending receipts: {e}")
        raise HTTPException(500, detail="Erro ao buscar comprovantes")


# ==========================================
# APROVAR TRANSAÇÃO
# ==========================================

@router.post("/approve-transaction/{transaction_id}")
async def approve_transaction(
    transaction_id: int,
    notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Aprova transação manualmente (Wise/Nomad).
    
    **Requer:** Admin role
    
    **Fluxo:**
    1. Atualiza status para 'paid'
    2. Estende período da assinatura
    3. Envia email de confirmação ao usuário
    4. Registra aprovação no log
    
    **Rate Limit:** 50/minuto
    """
    # TODO: Verificar se usuário é admin
    # TODO: Obter admin_id do token JWT
    admin_id = 1  # Placeholder
    
    try:
        from database.models import Transaction, Subscription
        
        # Buscar transação
        stmt = select(Transaction).where(Transaction.id == transaction_id)
        result = await db.execute(stmt)
        transaction = result.scalar_one_or_none()
        
        if not transaction:
            raise HTTPException(404, detail="Transação não encontrada")
        
        if transaction.status != "waiting_approval":
            raise HTTPException(400, detail="Transação não está aguardando aprovação")
        
        # Atualizar status
        transaction.status = "paid"
        transaction.updated_at = datetime.utcnow()
        
        # Se tem subscription associada, estender período
        if transaction.subscription_id:
            stmt = select(Subscription).where(Subscription.id == transaction.subscription_id)
            result = await db.execute(stmt)
            subscription = result.scalar_one_or_none()
            
            if subscription:
                # Determinar dias baseado no valor
                days = 365 if transaction.amount >= 500 else 30
                
                # Usar função SQL para estender
                from sqlalchemy import text
                await db.execute(
                    text("SELECT extend_subscription_period(:sub_id, :days)"),
                    {"sub_id": subscription.id, "days": days}
                )
        
        await db.commit()
        
        logger.info(
            f"Transaction approved",
            extra={
                "transaction_id": transaction_id,
                "admin_id": admin_id,
                "amount": float(transaction.amount)
            }
        )
        
        # TODO: Enviar email de confirmação
        
        return {
            "message": "Transação aprovada com sucesso",
            "transaction_id": transaction_id,
            "approved_at": datetime.utcnow().isoformat(),
            "approved_by": admin_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error approving transaction: {e}")
        raise HTTPException(500, detail="Erro ao aprovar transação")


# ==========================================
# REJEITAR TRANSAÇÃO
# ==========================================

@router.post("/reject-transaction/{transaction_id}")
async def reject_transaction(
    transaction_id: int,
    reason: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Rejeita transação manualmente.
    
    **Requer:** Admin role
    
    **Fluxo:**
    1. Atualiza status para 'failed'
    2. Registra motivo da rejeição
    3. Envia email ao usuário explicando
    
    **Rate Limit:** 50/minuto
    """
    # TODO: Verificar se usuário é admin
    admin_id = 1  # Placeholder
    
    try:
        from database.models import Transaction
        
        stmt = select(Transaction).where(Transaction.id == transaction_id)
        result = await db.execute(stmt)
        transaction = result.scalar_one_or_none()
        
        if not transaction:
            raise HTTPException(404, detail="Transação não encontrada")
        
        transaction.status = "failed"
        transaction.failure_reason = reason
        transaction.updated_at = datetime.utcnow()
        
        await db.commit()
        
        logger.info(
            f"Transaction rejected",
            extra={
                "transaction_id": transaction_id,
                "admin_id": admin_id,
                "reason": reason
            }
        )
        
        # TODO: Enviar email ao usuário
        
        return {
            "message": "Transação rejeitada",
            "transaction_id": transaction_id,
            "rejected_at": datetime.utcnow().isoformat(),
            "reason": reason
        }
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error rejecting transaction: {e}")
        raise HTTPException(500, detail="Erro ao rejeitar transação")


# ==========================================
# LISTAR TODAS AS TRANSAÇÕES
# ==========================================

@router.get("/transactions", response_model=TransactionListResponse)
async def list_all_transactions(
    status: Optional[str] = None,
    provider: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista todas as transações (admin).
    
    **Requer:** Admin role
    
    **Filtros:**
    - status: pending, paid, failed, waiting_approval, refunded
    - provider: stripe, asaas, opennode, wise, nomad
    
    **Rate Limit:** 50/minuto
    """
    # TODO: Verificar se usuário é admin
    
    try:
        from database.models import Transaction
        
        # Build query
        conditions = []
        if status:
            conditions.append(Transaction.status == status)
        if provider:
            conditions.append(Transaction.provider == provider)
        
        # Count
        count_stmt = select(func.count(Transaction.id))
        if conditions:
            count_stmt = count_stmt.where(and_(*conditions))
        
        total_result = await db.execute(count_stmt)
        total = total_result.scalar()
        
        # Fetch
        offset = (page - 1) * page_size
        stmt = select(Transaction).order_by(Transaction.created_at.desc())
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        stmt = stmt.offset(offset).limit(page_size)
        
        result = await db.execute(stmt)
        transactions = result.scalars().all()
        
        return TransactionListResponse(
            transactions=[
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
            ],
            total=total,
            page=page,
            page_size=page_size
        )
    
    except Exception as e:
        logger.error(f"Error listing transactions: {e}")
        raise HTTPException(500, detail="Erro ao listar transações")
