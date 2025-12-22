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

    async def create(self, dados: dict):
        """Cria um novo registro no histórico (usado pelo Webhook)"""
        from ..models import Historico
        # Mapeia campos do dict para o modelo
        historico = Historico(
            agendamento_id=dados.get('agendamento_id'),
            idoso_id=dados.get('idoso_id'),
            call_sid=dados.get('call_sid'),
            status=dados.get('status'),
            inicio=dados.get('inicio'),
            evento=dados.get('evento', 'Ligação Realizada')
        )
        self.db.add(historico)
        self.db.commit()
        self.db.refresh(historico)
        return historico.id

    async def update(self, id: int, dados: dict):
        """Atualiza registro existente"""
        from ..models import Historico
        historico = self.db.query(Historico).filter(Historico.id == id).first()
        if historico:
            for key, value in dados.items():
                if hasattr(historico, key):
                    setattr(historico, key, value)
            self.db.commit()
            return historico
        return None

    def list_all(self, skip: int = 0, limit: int = 100, idoso_id: int = None):
        """Lista histórico com filtros"""
        from ..models import Historico, Idoso
        query = self.db.query(Historico).join(Idoso)
        
        if idoso_id:
            query = query.filter(Historico.idoso_id == idoso_id)
            
        return query.order_by(Historico.criado_em.desc()).offset(skip).limit(limit).all()
