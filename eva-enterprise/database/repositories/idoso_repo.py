from sqlalchemy.orm import Session
from ..models import Idoso

class IdosoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, idoso_id: int) -> Idoso:
        return self.db.query(Idoso).filter(Idoso.id == idoso_id).first()

    def get_by_telefone(self, telefone: str) -> Idoso:
        return self.db.query(Idoso).filter(Idoso.telefone == telefone).first()
