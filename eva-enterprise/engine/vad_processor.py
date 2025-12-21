"""
VAD Processor - Voice Activity Detection
Substitui RMS puro para evitar falsos positivos com TV/rádio
"""
import webrtcvad
import audioop
from typing import Optional


class VADProcessor:
    """
    Filtro de Voice Activity Detection inteligente
    Diferencia voz humana de ruído ambiente (TV, rádio, etc)
    """
    
    def __init__(self, sample_rate: int = 16000, aggressiveness: int = 3):
        """
        Args:
            sample_rate: Taxa de amostragem do áudio (8000, 16000, 32000, 48000 Hz)
            aggressiveness: Nível de agressividade do VAD (0-3)
                0 = Menos agressivo (aceita mais sons como fala)
                3 = Mais agressivo (mais rigoroso, ideal para ambientes ruidosos)
        """
        self.vad = webrtcvad.Vad(aggressiveness)
        self.sample_rate = sample_rate
        self.aggressiveness = aggressiveness
        
        # Valida sample rate suportado
        if sample_rate not in [8000, 16000, 32000, 48000]:
            raise ValueError(f"Sample rate {sample_rate} não suportado. Use: 8000, 16000, 32000 ou 48000")
    
    def is_speech(self, audio_chunk: bytes) -> bool:
        """
        Detecta se o chunk de áudio contém VOZ HUMANA
        
        Args:
            audio_chunk: Bytes PCM de áudio (deve ter duração de 10, 20 ou 30ms)
        
        Returns:
            True se for fala humana, False caso contrário
        """
        try:
            # webrtcvad exige chunks de 10, 20 ou 30ms
            # Para 16kHz: 10ms = 320 bytes, 20ms = 640 bytes, 30ms = 960 bytes
            return self.vad.is_speech(audio_chunk, self.sample_rate)
        
        except Exception as e:
            print(f"⚠️ VAD falhou: {e}. Usando fallback RMS.")
            return self._fallback_rms(audio_chunk)
    
    def _fallback_rms(self, audio_chunk: bytes, threshold: int = 300) -> bool:
        """
        Fallback para detecção por RMS se VAD falhar
        
        Args:
            audio_chunk: Bytes de áudio PCM
            threshold: Limiar RMS para considerar como fala
        
        Returns:
            True se RMS > threshold
        """
        try:
            rms = audioop.rms(audio_chunk, 2)  # 2 = 16-bit samples
            return rms > threshold
        except Exception as e:
            print(f"❌ Fallback RMS também falhou: {e}")
            return False
    
    def adjust_aggressiveness(self, ambiente_ruidoso: bool):
        """
        Ajusta agressividade dinamicamente baseado no perfil do idoso
        
        Args:
            ambiente_ruidoso: True se idoso mora sozinho ou com TV alta
        """
        new_level = 3 if ambiente_ruidoso else 2
        if new_level != self.aggressiveness:
            self.aggressiveness = new_level
            self.vad.set_mode(new_level)
            print(f"🔧 VAD ajustado para nível {new_level}")
    
    @staticmethod
    def validate_chunk_duration(audio_chunk: bytes, sample_rate: int) -> Optional[str]:
        """
        Valida se o chunk tem duração válida para webrtcvad (10, 20 ou 30ms)
        
        Returns:
            None se válido, mensagem de erro caso contrário
        """
        # 16-bit samples = 2 bytes por sample
        num_samples = len(audio_chunk) // 2
        duration_ms = (num_samples / sample_rate) * 1000
        
        valid_durations = [10, 20, 30]
        if not any(abs(duration_ms - valid) < 1 for valid in valid_durations):
            return f"Chunk inválido: {duration_ms:.1f}ms (precisa ser 10, 20 ou 30ms)"
        
        return None


class VADBufferManager:
    """
    Gerencia buffer de áudio para garantir chunks no tamanho correto para VAD
    """
    
    def __init__(self, sample_rate: int = 16000, target_duration_ms: int = 20):
        """
        Args:
            sample_rate: Taxa de amostragem
            target_duration_ms: Duração alvo dos chunks (10, 20 ou 30ms)
        """
        self.sample_rate = sample_rate
        self.target_duration_ms = target_duration_ms
        
        # Calcula tamanho do chunk em bytes
        samples_per_chunk = int(sample_rate * target_duration_ms / 1000)
        self.chunk_size = samples_per_chunk * 2  # 2 bytes por sample (16-bit)
        
        self.buffer = b""
    
    def add_audio(self, audio_data: bytes) -> list[bytes]:
        """
        Adiciona áudio ao buffer e retorna chunks completos
        
        Args:
            audio_data: Bytes de áudio recebidos
        
        Returns:
            Lista de chunks prontos para VAD
        """
        self.buffer += audio_data
        
        chunks = []
        while len(self.buffer) >= self.chunk_size:
            chunk = self.buffer[:self.chunk_size]
            chunks.append(chunk)
            self.buffer = self.buffer[self.chunk_size:]
        
        return chunks
    
    def clear(self):
        """Limpa o buffer"""
        self.buffer = b""