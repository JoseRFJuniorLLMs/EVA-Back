from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, JSON, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from .connection import Base
from utils.wise_generator import WiseReferenceGenerator

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    amount = Column(Numeric(10, 2))
    currency = Column(String(3))
    provider = Column(String(50)) # stripe, asaas, wise, opennode
    status = Column(String(20)) # paid, pending, failed, waiting_approval
    external_ref = Column(String(255), unique=True)
    failure_reason = Column(String(255))
    proof_url = Column(String(500)) 
    
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
    metadata_json = Column(JSON, default={})
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    subscription = relationship("Subscription", back_populates="transactions")

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    plan_tier = Column(String(50)) 
    status = Column(String(20)) 
    payment_method_default = Column(String(50))
    
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    external_subscription_id = Column(String(255))
    
    metadata_json = Column(JSON, default={})
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    transactions = relationship("Transaction", back_populates="subscription")
    wise_references = relationship("WisePaymentReference", back_populates="subscription")

class PaymentInstruction(Base):
    """
    Model para instruções de pagamento (v30_payment_instructions.sql)
    """
    __tablename__ = "payment_instructions"
    
    id = Column(Integer, primary_key=True)
    provider = Column(String(20)) # wise, nomad
    currency = Column(String(3))
    details_json = Column(JSON, nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WisePaymentReference(Base):
    __tablename__ = "wise_payment_references"
    
    id = Column(Integer, primary_key=True)
    reference_code = Column(String(50), unique=True, nullable=False, index=True)
    
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
    
    expected_amount = Column(Numeric(10, 2), nullable=False)
    expected_currency = Column(String(3), nullable=False)
    plan_tier = Column(String(20), nullable=False)
    
    status = Column(String(20), default="pending")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    
    metadata_json = Column(JSON, default={})
    
    subscription = relationship("Subscription", back_populates="wise_references")
    
    @staticmethod
    def generate_for_user(user_id: int, amount: float, currency: str, plan_tier: str):
        reference_code = WiseReferenceGenerator.generate(user_id, "USER")
        return WisePaymentReference(
            reference_code=reference_code,
            user_id=user_id,
            expected_amount=amount,
            expected_currency=currency,
            plan_tier=plan_tier,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
    
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at
    
    def mark_as_used(self, subscription_id: int):
        self.status = "used"
        self.used_at = datetime.utcnow()
        self.subscription_id = subscription_id


class WebhookLog(Base):
    """
    Log de webhooks recebidos para auditoria e debug.
    """
    __tablename__ = "webhook_logs"

    id = Column(Integer, primary_key=True)
    provider = Column(String(50), nullable=False, index=True)  # stripe, asaas, opennode, wise
    event_type = Column(String(100), nullable=False, index=True)
    event_id = Column(String(255), nullable=True)  # ID unico do evento no provider
    payload = Column(JSON, nullable=False)  # Payload completo
    status = Column(String(20), default="received")  # received, processing, processed, failed, ignored
    error_message = Column(Text, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    processed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<WebhookLog {self.provider}/{self.event_type} ({self.status})>"


class PaymentAuditLog(Base):
    """
    Log de auditoria de acoes em pagamentos.
    """
    __tablename__ = "payment_audit_logs"

    id = Column(Integer, primary_key=True)
    action = Column(String(50), nullable=False)  # create, update, approve, reject, refund
    entity_type = Column(String(50), nullable=False)  # transaction, subscription
    entity_id = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    admin_id = Column(Integer, nullable=True)  # ID do admin que realizou acao
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<PaymentAuditLog {self.action} {self.entity_type}:{self.entity_id}>"
