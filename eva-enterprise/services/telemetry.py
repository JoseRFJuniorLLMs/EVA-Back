"""
Telemetry Service - Registra métricas de qualidade das ligações
"""
from typing import Optional
from database.connection import SessionLocal
from database.repositories.historico_repo import HistoricoRepository


class TelemetryService:
    def __init__(self):
        self.historico_repo = None
    
    def _get_repo(self):
        """Lazy initialization do repositório"""
        if not self.historico_repo:
            db = SessionLocal()
            self.historico_repo = HistoricoRepository(db)
        return self.historico_repo
    
    @staticmethod
    def log_latency(ms: int):
        # Placeholder for telemetry logging
        pass

    @staticmethod
    def log_error(context: str, error: str):
        print(f"[TELEMETRY] Error in {context}: {error}")
    
    async def log_call_telemetry(
        self,
        ligacao_id: str,
        qualidade_audio: str,
        interrupcoes: int,
        latencia_media_ms: int,
        packets_perdidos: int = 0,
        vad_false_positives: int = 0  # Conta "falsos positivos" da TV
    ):
        """
        Registra métricas de telemetria da ligação.
        
        Args:
            ligacao_id: ID da ligação no histórico
            qualidade_audio: 'excelente', 'boa', 'regular', 'ruim'
            interrupcoes: Número de interrupções detectadas
            latencia_media_ms: Latência média em milissegundos
            packets_perdidos: Número de pacotes de áudio perdidos
            vad_false_positives: Falsos positivos do VAD (ex: TV, rádio)
        """
        repo = self._get_repo()
        await repo.update(ligacao_id, {
            'qualidade_audio': qualidade_audio,
            'interrupcoes_detectadas': interrupcoes,
            'latencia_media_ms': latencia_media_ms,
            'packets_perdidos': packets_perdidos,
            'vad_false_positives': vad_false_positives
        })


# Instância global do serviço
telemetry_service = TelemetryService()
