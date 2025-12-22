from sqlalchemy.orm import Session
from ..models import Pagamento, AuditLog
from typing import List, Optional
import datetime

class PagamentoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_pagamentos(self, limit: int = 50, status: str = None) -> List[Pagamento]:
        query = self.db.query(Pagamento)
        if status:
            query = query.filter(Pagamento.status == status)
        return query.order_by(Pagamento.data.desc()).limit(limit).all()

    def create_pagamento(self, dados: dict) -> Pagamento:
        pagamento = Pagamento(**dados)
        self.db.add(pagamento)
        self.db.commit()
        self.db.refresh(pagamento)
        return pagamento

    def get_by_id(self, id: int) -> Optional[Pagamento]:
        return self.db.query(Pagamento).filter(Pagamento.id == id).first()

class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def log_action(self, acao: str, usuario: str, detalhes: dict) -> AuditLog:
        log = AuditLog(acao=acao, usuario=usuario, detalhes=detalhes)
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get_logs(self, limit: int = 100, usuario: str = None) -> List[AuditLog]:
        query = self.db.query(AuditLog)
        if usuario:
            query = query.filter(AuditLog.usuario == usuario)
        return query.order_by(AuditLog.data.desc()).limit(limit).all()

    def get_by_id(self, id: int) -> Optional[AuditLog]:
        return self.db.query(AuditLog).filter(AuditLog.id == id).first()
