from sqlalchemy.orm import Session
from ..models import Alerta
import datetime

class HistoricoRepository:
    def __init__(self, db: Session):
        self.db = db

    def criar_alerta(self, tipo: str, descricao: str):
        novo_alerta = Alerta(tipo=tipo, descricao=descricao, criado_em=datetime.datetime.now())
        self.db.add(novo_alerta)
        self.db.commit()
        self.db.refresh(novo_alerta)
        return novo_alerta
