from database.connection import SessionLocal
from database.repositories.historico_repo import HistoricoRepository

class AlertsHandler:
    def __init__(self):
        self.palavras_alerta = [
            "dor", "mal", "tontura", "tonto", "zonzo", "peito", "coração",
            "falta de ar", "respirar", "cabeça", "ajuda", "socorro",
            "fraco", "fraca", "cansado", "cansada"
        ]

    def check_for_alerts(self, text: str, agendamento_id: int = None):
        if not text or not agendamento_id:
            return

        texto_lower = text.lower()
        for palavra in self.palavras_alerta:
            if palavra in texto_lower:
                self._registrar_alerta(
                    "PASSA_MAL",
                    f"Agendamento #{agendamento_id} mencionou: '{text}'"
                )
                break

    def _registrar_alerta(self, tipo: str, descricao: str):
        db = SessionLocal()
        try:
            repo = HistoricoRepository(db)
            repo.criar_alerta(tipo, descricao)
            print(f"🚨 ALERTA REGISTRADO: {tipo} - {descricao}")
        finally:
            db.close()
