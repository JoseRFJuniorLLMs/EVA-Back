from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy import select, delete
from ..models import Alerta, Idoso, Cuidador, PsicologiaInsight, TopicoAfetivo
from services.notification_service import NotificationService
from typing import List, Optional
import datetime

class AlertaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_recent_alerts(self, limit: int = 50, tipo: str = None) -> List[dict]:
        query = select(Alerta, Idoso.nome.label("idoso_nome"), Idoso.foto_url, Idoso.telefone).join(Idoso, Alerta.idoso_id == Idoso.id)
        if tipo:
            query = query.filter(Alerta.tipo == tipo)
        result = await self.db.execute(query.order_by(Alerta.criado_em.desc()).limit(limit))
        
        alertas = []
        for row in result:
            res = {c.name: getattr(row.Alerta, c.name) for c in row.Alerta.__table__.columns}
            res["idoso_nome"] = row.idoso_nome
            res["foto_url"] = row.foto_url
            res["telefone"] = row.telefone
            alertas.append(res)
        return alertas

    async def create_alerta(self, idoso_id: int, tipo: str, severidade: str, mensagem: str, destinatarios: list = []) -> Alerta:
        alerta = Alerta(
            idoso_id=idoso_id,
            tipo=tipo,
            severidade=severidade,
            mensagem=mensagem,
            destinatarios=destinatarios
        )
        self.db.add(alerta)
        await self.db.commit()
        await self.db.refresh(alerta)
        
        # Enviar notificações push se for relevante
        if severidade in ['critica', 'alta'] or "RISCO" in severidade.upper():
            await self._notify_family(alerta)
            
        return alerta

    async def _notify_family(self, alerta: Alerta):
        """Busca tokens de dispositivos e envia push"""
        try:
            # 1. Buscar cuidadores/familiares com token ativo
            query = select(Cuidador).where(
                Cuidador.idoso_id == alerta.idoso_id,
                Cuidador.ativo == True,
                Cuidador.device_token.isnot(None)
            )
            result = await self.db.execute(query)
            cuidadores = result.scalars().all()
            
            tokens = [c.device_token for c in cuidadores if c.device_token]
            
            # TODO: Buscar também na tabela Familiares se tiver token lá
            
            if tokens:
                notifier = NotificationService()
                notifier.send_multicast_notification(
                    tokens=tokens,
                    title=f"🚨 EVA Alerta - {alerta.severidade.upper()}",
                    body=alerta.mensagem[:100], # Trucar msg muito longa
                    data={
                        "alerta_id": str(alerta.id),
                        "tipo": alerta.tipo,
                        "idoso_id": str(alerta.idoso_id),
                        "click_action": "FLUTTER_NOTIFICATION_CLICK"
                    }
                )
        except Exception as e:
            print(f"Erro ao enviar notificação push: {e}")

    async def get_by_id(self, id: int) -> Optional[dict]:
        query = select(Alerta, Idoso.nome.label("idoso_nome"), Idoso.foto_url, Idoso.telefone).join(Idoso, Alerta.idoso_id == Idoso.id).filter(Alerta.id == id)
        result = await self.db.execute(query)
        row = result.first()
        if row:
            res = {c.name: getattr(row.Alerta, c.name) for c in row.Alerta.__table__.columns}
            res["idoso_nome"] = row.idoso_nome
            res["foto_url"] = row.foto_url
            res["telefone"] = row.telefone
            return res
        return None

    async def resolve_alerta(self, id: int, nota: str = None) -> Optional[Alerta]:
        alerta = await self.get_by_id(id)
        if alerta:
            alerta.resolvido = True
            alerta.data_resolucao = datetime.datetime.now()
            alerta.resolucao_nota = nota
            await self.db.commit()
            await self.db.refresh(alerta)
        return alerta

    # Insights
    async def get_insights(self, idoso_id: int) -> List[PsicologiaInsight]:
        query = select(PsicologiaInsight).filter(PsicologiaInsight.idoso_id == idoso_id).order_by(PsicologiaInsight.data_insight.desc())
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_insight(self, idoso_id: int, mensagem: str, tipo: str = 'positivo', relevancia: str = 'media') -> PsicologiaInsight:
        insight = PsicologiaInsight(idoso_id=idoso_id, mensagem=mensagem, tipo=tipo, relevancia=relevancia)
        self.db.add(insight)
        await self.db.commit()
        await self.db.refresh(insight)
        return insight

    # Topicos Afetivos
    async def get_topicos(self, idoso_id: int) -> List[TopicoAfetivo]:
        query = select(TopicoAfetivo).filter(TopicoAfetivo.idoso_id == idoso_id).order_by(TopicoAfetivo.frequencia.desc())
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_topico(self, idoso_id: int, topico: str, sentimento: str = None) -> TopicoAfetivo:
        query = select(TopicoAfetivo).filter(
            TopicoAfetivo.idoso_id == idoso_id,
            TopicoAfetivo.topico == topico
        )
        result = await self.db.execute(query)
        existing = result.scalar_one_or_none()

        if existing:
            existing.frequencia += 1
            existing.ultima_mencao = datetime.datetime.now()
            if sentimento:
                existing.sentimento_associado = sentimento
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            new_topic = TopicoAfetivo(idoso_id=idoso_id, topico=topico, sentimento_associado=sentimento)
            self.db.add(new_topic)
            await self.db.commit()
            await self.db.refresh(new_topic)
            return new_topic
