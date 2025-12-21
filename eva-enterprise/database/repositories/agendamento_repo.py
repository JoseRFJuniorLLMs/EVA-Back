from sqlalchemy.orm import Session
from database.connection import SessionLocal  # Caminho correto
from ..models import Agendamento, Idoso  # Vamos criar isso logo em seguida

class AgendamentoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, agendamento_id: int) -> Agendamento:
        return self.db.query(Agendamento).filter(Agendamento.id == agendamento_id).first()

    def update_status(self, agendamento_id: int, status: str):
        agendamento = self.get_by_id(agendamento_id)
        if agendamento:
            agendamento.status = status
            self.db.commit()
            self.db.refresh(agendamento)
        return agendamento

    def get_details_with_idoso(self, agendamento_id: int):
        return self.db.query(Agendamento).join(Idoso).filter(Agendamento.id == agendamento_id).first()