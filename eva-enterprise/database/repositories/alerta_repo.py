from sqlalchemy.orm import Session
from ..models import Alerta, PsicologiaInsight, TopicoAfetivo
from typing import List, Optional
import datetime

class AlertaRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_recent_alerts(self, limit: int = 50, tipo: str = None) -> List[Alerta]:
        query = self.db.query(Alerta)
        if tipo:
            query = query.filter(Alerta.tipo == tipo)
        return query.order_by(Alerta.criado_em.desc()).limit(limit).all()

    def create_alerta(self, tipo: str, descricao: str) -> Alerta:
        alerta = Alerta(tipo=tipo, descricao=descricao)
        self.db.add(alerta)
        self.db.commit()
        self.db.refresh(alerta)
        return alerta

    def get_by_id(self, id: int) -> Optional[Alerta]:
        return self.db.query(Alerta).filter(Alerta.id == id).first()

    def resolve_alerta(self, id: int) -> Optional[Alerta]:
        alerta = self.get_by_id(id)
        if alerta:
            alerta.status = 'resolvido'
            self.db.commit()
            self.db.refresh(alerta)
        return alerta

    # Insights
    def get_insights(self, idoso_id: int) -> List[PsicologiaInsight]:
        return self.db.query(PsicologiaInsight).filter(PsicologiaInsight.idoso_id == idoso_id).order_by(PsicologiaInsight.data_geracao.desc()).all()

    def create_insight(self, idoso_id: int, conteudo: str, relevancia: int) -> PsicologiaInsight:
        insight = PsicologiaInsight(idoso_id=idoso_id, conteudo=conteudo, relevancia=relevancia)
        self.db.add(insight)
        self.db.commit()
        self.db.refresh(insight)
        return insight

    # Topicos Afetivos
    def get_topicos(self, idoso_id: int) -> List[TopicoAfetivo]:
        return self.db.query(TopicoAfetivo).filter(TopicoAfetivo.idoso_id == idoso_id).order_by(TopicoAfetivo.frequencia.desc()).all()

    def update_topico(self, idoso_id: int, topico: str) -> TopicoAfetivo:
        # Check if exists
        existing = self.db.query(TopicoAfetivo).filter(
            TopicoAfetivo.idoso_id == idoso_id,
            TopicoAfetivo.topico == topico
        ).first()

        if existing:
            existing.frequencia += 1
            existing.ultima_mencao = datetime.datetime.now()
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            new_topic = TopicoAfetivo(idoso_id=idoso_id, topico=topico)
            self.db.add(new_topic)
            self.db.commit()
            self.db.refresh(new_topic)
            return new_topic
