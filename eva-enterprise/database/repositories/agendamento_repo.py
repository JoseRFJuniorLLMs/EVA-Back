from sqlalchemy.orm import Session
from ..models import Agendamento, Idoso
from typing import List, Optional
import datetime

class AgendamentoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, agendamento_id: int) -> Optional[Agendamento]:
        return self.db.query(Agendamento).filter(Agendamento.id == agendamento_id).first()

    def get_all(self, skip: int = 0, limit: int = 100, idoso_id: int = None) -> List[Agendamento]:
        query = self.db.query(Agendamento)
        if idoso_id:
            query = query.filter(Agendamento.idoso_id == idoso_id)
        return query.order_by(Agendamento.horario.desc()).offset(skip).limit(limit).all()

    def create(self, dados: dict) -> Agendamento:
        agendamento = Agendamento(**dados)
        self.db.add(agendamento)
        self.db.commit()
        self.db.refresh(agendamento)
        return agendamento

    def update(self, id: int, dados: dict) -> Optional[Agendamento]:
        agendamento = self.get_by_id(id)
        if agendamento:
            for k, v in dados.items():
                if v is not None:
                    setattr(agendamento, k, v)
            self.db.commit()
            self.db.refresh(agendamento)
        return agendamento

    def delete(self, id: int) -> bool:
        agendamento = self.get_by_id(id)
        if agendamento:
            self.db.delete(agendamento)
            self.db.commit()
            return True
        return False

    def update_status(self, agendamento_id: int, status: str) -> Optional[Agendamento]:
        return self.update(agendamento_id, {'status': status})

    def get_details_with_idoso(self, agendamento_id: int):
        return self.db.query(Agendamento, Idoso).join(Idoso).filter(Agendamento.id == agendamento_id).first()

    def get_pending_calls(self) -> List[Agendamento]:
        # Logic to find pending calls that are due
        now = datetime.datetime.now()
        return self.db.query(Agendamento).filter(
            Agendamento.status == 'pendente',
            Agendamento.horario <= now
        ).all()