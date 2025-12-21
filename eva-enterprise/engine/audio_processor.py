"""
Audio Processor - Processamento de áudio com VAD inteligente (REFATORADO)
Substitui RMS puro por webrtcvad para evitar falsos positivos
"""
import asyncio
import audioop
import base64
import time
from typing import Callable, Optional
from engine.vad_processor import VADProcessor, VADBufferManager

# Tenta importar webrtcvad se disponível
try:
    import webrtcvad
    WEBRTCVAD_AVAILABLE = True
except ImportError:
    WEBRTCVAD_AVAILABLE = False
    print("⚠️ webrtcvad não disponível, usando VADProcessor padrão")


class AudioProcessor:
    """
    Processa stream de áudio do Twilio com detecção inteligente de fala
    """
    
    def __init__(
        self,
        context: dict,
        session = None,
        on_turn_complete: Optional[Callable] = None
    ):
        """
        Args:
            context: Contexto da ligação (com configs de áudio personalizadas)
            session: Sessão do Gemini (opcional, pode ser setada depois)
            on_turn_complete: Callback quando usuário termina de falar
        """
        self.session = session
        self.context = context
        self.on_turn_complete = on_turn_complete

    def set_session(self, session):
        """Define sessão do Gemini após inicialização"""
        self.session = session
        
        # Configs de áudio personalizadas (vem do contexto, não hardcoded)
        audio_config = context.get('audio_config', {})
        self.silence_threshold = audio_config.get('silence_threshold', 0.8)
        self.speech_rms = audio_config.get('speech_rms', 300)
        self.buffer_size = audio_config.get('buffer_size', 1600)
        
        # VAD inteligente
        ambiente_ruidoso = context.get('metadata', {}).get('ambiente_ruidoso', False)
        aggressiveness = 3 if ambiente_ruidoso else 2
        
        # WebRTC VAD nativo se disponível
        if WEBRTCVAD_AVAILABLE:
            self.webrtc_vad = webrtcvad.Vad(aggressiveness)
        else:
            self.webrtc_vad = None
        
        self.vad = VADProcessor(
            sample_rate=16000,
            aggressiveness=aggressiveness
        )
        
        self.vad_buffer = VADBufferManager(
            sample_rate=16000,
            target_duration_ms=20
        )
        
        # Estado da conversa
        self.is_speaking = False
        self.last_speech_time = 0
        self.user_turn_ended = False
        self.accumulated_text = ""
        
        # Guarda-corpos para end-of-turn
        self.max_turn_duration = 30  # Timeout máximo de turno (segundos)
        self.turn_start_time = None
        self.end_of_turn_sent = False  # Previne duplicação
        
        # Telemetria
        self.vad_false_positives = 0  # Conta "falsos positivos" (RMS alto, VAD rejeitou)
        self.total_chunks_processed = 0
        
        # Monitoramento e Otimização
        self.quality_monitor = AudioQualityMonitor()
        self.buffer_optimizer = AudioBufferOptimizer(initial_size=self.buffer_size)
        
        print(f"🎙️ AudioProcessor inicializado:")
        print(f"   - Silence threshold: {self.silence_threshold}s")
        print(f"   - Speech RMS: {self.speech_rms}")
        print(f"   - VAD aggressiveness: {aggressiveness}")
        print(f"   - Max turn duration: {self.max_turn_duration}s")
        print(f"   - WebRTC VAD: {'✓' if WEBRTCVAD_AVAILABLE else '✗'}")
    
    async def process_audio_chunk(self, audio_chunk: bytes) -> bool:
        """
        Processa chunk com VAD inteligente (dupla validação)
        
        Args:
            audio_chunk: Bytes de áudio PCM 16kHz
            
        Returns:
            True se detectou fala, False se silêncio/ruído
        """
        self.total_chunks_processed += 1
        
        # 1. Primeiro filtro: RMS básico (rápido)
        threshold = self.speech_rms
        try:
            rms = audioop.rms(audio_chunk, 2)
        except Exception:
            rms = 0
        
        if rms < threshold:
            return False  # Claramente silêncio
        
        # 2. Segundo filtro: VAD inteligente (evita TV/ruído)
        is_speech = False
        
        if self.webrtc_vad:
            # WebRTC VAD precisa de frames de 10, 20 ou 30ms
            frame_duration_ms = 30
            sample_rate = 16000
            frame_size = int(sample_rate * frame_duration_ms / 1000) * 2  # 2 bytes por sample
            
            # Processa frame por frame
            for i in range(0, len(audio_chunk), frame_size):
                frame = audio_chunk[i:i+frame_size]
                if len(frame) == frame_size:
                    try:
                        if self.webrtc_vad.is_speech(frame, sample_rate):
                            is_speech = True
                            break
                    except Exception:
                        # Fallback para RMS se VAD falhar
                        is_speech = True
        else:
            # Fallback para VADProcessor
            is_speech = self.vad.is_speech(audio_chunk)
        
        # 3. Telemetria: conta "falso positivo" (RMS alto mas VAD rejeitou)
        if rms >= threshold and not is_speech:
            self.vad_false_positives += 1
            self.quality_monitor.record_false_positive()
        
        self.quality_monitor.record_chunk(is_speech)
        return is_speech
    
    async def process_twilio_stream(self, twilio_ws):
        """
        Processa stream de áudio do Twilio
        """
        async for message in twilio_ws.iter_json():
            event = message.get("event")
            
            if event == "media":
                audio_data = message["media"]["payload"]
                await self._process_audio_chunk(audio_data)
            
            elif event == "stop":
                print("🛑 Stream do Twilio encerrado")
                break
    
    async def _process_audio_chunk(self, audio_payload: str):
        """
        Processa chunk de áudio individual
        """
        # Decodifica áudio (base64 -> bytes)
        audio_bytes = base64.b64decode(audio_payload)
        
        # Adiciona ao buffer do VAD para garantir tamanho correto
        chunks = self.vad_buffer.add_audio(audio_bytes)
        
        for chunk in chunks:
            await self._analyze_chunk(chunk)
    
    async def _analyze_chunk(self, audio_chunk: bytes):
        """
        Analisa chunk usando VAD inteligente com guarda-corpos
        """
        # Usa processamento com dupla validação
        is_speech = await self.process_audio_chunk(audio_chunk)
        current_time = time.time()
        
        if is_speech:
            if not self.is_speaking:
                print(f"🎤 [USER] Começou a falar (VAD confirmado)")
                self.is_speaking = True
                self.user_turn_ended = False
                self.end_of_turn_sent = False  # Reset flag
                self.turn_start_time = current_time  # Marca início do turno
            
            self.last_speech_time = current_time
            
            # Envia áudio para o Gemini
            await self.session.send(input=audio_chunk)
        
        elif self.is_speaking:
            # Usuário parou de falar - verifica silêncio
            silence_duration = current_time - self.last_speech_time
            turn_duration = current_time - (self.turn_start_time or current_time)
            
            # Condição normal: silêncio detectado
            should_end = (
                silence_duration > self.silence_threshold and 
                not self.user_turn_ended and
                not self.end_of_turn_sent
            )
            
            # Guarda-corpo: timeout do turno (evita travamento)
            timeout_exceeded = turn_duration > self.max_turn_duration
            
            if should_end or timeout_exceeded:
                await self._send_end_of_turn(
                    reason="silence" if should_end else "timeout",
                    silence_duration=silence_duration,
                    turn_duration=turn_duration
                )
    
    async def _send_end_of_turn(
        self, 
        reason: str,
        silence_duration: float = 0,
        turn_duration: float = 0
    ):
        """
        Envia end-of-turn com logging detalhado e proteção contra duplicação.
        """
        # Previne duplicação
        if self.end_of_turn_sent:
            print(f"⚠️ [EOT] Já enviado, ignorando duplicação")
            return
        
        print(f"🔇 [USER] Fim do turno ({reason})")
        print(f"   - Silêncio: {silence_duration:.1f}s")
        print(f"   - Duração total: {turn_duration:.1f}s")
        
        try:
            # Envia com timeout para evitar travamento
            await asyncio.wait_for(
                self.session.send(input="", end_of_turn=True),
                timeout=2.0
            )
            
            # Atualiza estado
            self.end_of_turn_sent = True
            self.user_turn_ended = True
            self.is_speaking = False
            
            print("   ✓ End-of-turn enviado ao Gemini")
            
            # Callback para salvar checkpoint
            if self.on_turn_complete:
                await self.on_turn_complete(self.accumulated_text)
            
            # Reseta acumulador
            self.accumulated_text = ""
        
        except asyncio.TimeoutError:
            print("   ✗ Timeout ao enviar end-of-turn!")
            self.end_of_turn_sent = True  # Marca como enviado para evitar retry infinito
        
        except Exception as e:
            print(f"   ✗ Erro ao enviar end-of-turn: {e}")
            self.end_of_turn_sent = True  # Marca como enviado para evitar retry infinito
    
    def update_accumulated_text(self, text: str):
        """
        Atualiza texto acumulado da transcrição do usuário
        """
        self.accumulated_text += " " + text
    
    def update_latency(self, latency_ms: float):
        """Atualiza latência e otimiza buffer"""
        self.buffer_optimizer.record_latency(latency_ms)
        new_size = self.buffer_optimizer.get_optimal_size()
        if new_size != self.buffer_size:
            print(f"⚖️ [BUFFER] Ajustando tamanho: {self.buffer_size} -> {new_size}")
            self.buffer_size = new_size

    def get_telemetry(self) -> dict:
        """
        Retorna métricas de telemetria do VAD
        """
        return {
            'total_chunks': self.total_chunks_processed,
            'vad_false_positives': self.vad_false_positives,
            'false_positive_rate': self.vad_false_positives / max(self.total_chunks_processed, 1)
        }

    # Métodos de conversão de áudio (Wrapper para audioop)
    def ratecv_24k_to_8k(self, audio: bytes) -> bytes:
        """Converte 24kHz para 8kHz"""
        try:
            return audioop.ratecv(audio, 2, 1, 24000, 8000, None)[0]
        except Exception as e:
            print(f"Erro conversão 24k->8k: {e}")
            return audio

    def lin2ulaw(self, audio: bytes) -> bytes:
        """Converte PCM linear para u-law"""
        try:
            return audioop.lin2ulaw(audio, 2)
        except Exception as e:
            print(f"Erro lin2ulaw: {e}")
            return audio

    def ulaw2lin(self, audio: bytes) -> bytes:
        """Converte u-law para PCM linear"""
        try:
            return audioop.ulaw2lin(audio, 2)
        except Exception as e:
            print(f"Erro ulaw2lin: {e}")
            return audio

    def ratecv_8k_to_16k(self, audio: bytes) -> bytes:
        """Converte 8kHz para 16kHz"""
        try:
            return audioop.ratecv(audio, 2, 1, 8000, 16000, None)[0]
        except Exception as e:
            print(f"Erro conversão 8k->16k: {e}")
            return audio


class AudioQualityMonitor:
    """
    Monitor de qualidade do áudio para telemetria
    """
    
    def __init__(self):
        self.total_chunks = 0
        self.speech_chunks = 0
        self.silence_chunks = 0
        self.interruptions = 0
        self.vad_false_positives = 0  # Telemetria de falsos positivos
        self.start_time = time.time()
    
    def record_chunk(self, is_speech: bool):
        """
        Registra chunk processado
        """
        self.total_chunks += 1
        
        if is_speech:
            self.speech_chunks += 1
        else:
            self.silence_chunks += 1
    
    def record_interruption(self):
        """
        Registra interrupção detectada
        """
        self.interruptions += 1
    
    def record_false_positive(self):
        """
        Registra falso positivo do VAD (TV, rádio, etc)
        """
        self.vad_false_positives += 1
    
    def get_metrics(self) -> dict:
        """
        Retorna métricas de qualidade
        """
        duration = time.time() - self.start_time
        
        return {
            'duracao_segundos': int(duration),
            'total_chunks': self.total_chunks,
            'speech_chunks': self.speech_chunks,
            'silence_chunks': self.silence_chunks,
            'interrupcoes': self.interruptions,
            'vad_false_positives': self.vad_false_positives,
            'speech_ratio': self.speech_chunks / max(self.total_chunks, 1),
            'qualidade_audio': self._calculate_quality()
        }
    
    def _calculate_quality(self) -> str:
        """
        Calcula qualidade geral do áudio
        """
        if self.total_chunks == 0:
            return 'desconhecida'
        
        speech_ratio = self.speech_chunks / self.total_chunks
        
        if speech_ratio > 0.7:
            return 'ruim'  # Muito ruído detectado como fala
        elif speech_ratio > 0.3:
            return 'boa'
        else:
            return 'excelente'


class AudioBufferOptimizer:
    """
    Otimiza tamanho do buffer baseado em latência observada
    """
    
    def __init__(self, initial_size: int = 1600):
        self.current_size = initial_size
        self.latency_history = []
        self.max_history = 50
    
    def record_latency(self, latency_ms: float):
        """
        Registra latência observada
        """
        self.latency_history.append(latency_ms)
        
        if len(self.latency_history) > self.max_history:
            self.latency_history.pop(0)
    
    def get_optimal_size(self) -> int:
        """
        Calcula tamanho ótimo do buffer
        """
        if not self.latency_history:
            return self.current_size
        
        avg_latency = sum(self.latency_history) / len(self.latency_history)
        
        # Se latência alta (>500ms), aumenta buffer
        if avg_latency > 500:
            self.current_size = min(self.current_size + 200, 3200)
        
        # Se latência baixa (<200ms), diminui buffer
        elif avg_latency < 200:
            self.current_size = max(self.current_size - 200, 800)
        
        return self.current_size


class SpeechDetector:
    """
    Detector de fala com dupla validação (VAD + RMS)
    """
    
    def __init__(self, vad: VADProcessor, rms_threshold: int):
        self.vad = vad
        self.rms_threshold = rms_threshold
        self.vad_false_positives = 0  # Telemetria
        
        # WebRTC VAD se disponível
        if WEBRTCVAD_AVAILABLE:
            self.webrtc_vad = webrtcvad.Vad(2)
        else:
            self.webrtc_vad = None
    
    def is_speech(self, audio_chunk: bytes) -> bool:
        """
        Detecta fala usando VAD como primário e RMS como fallback
        """
        # 1. Primeiro filtro: RMS
        rms = self._get_rms(audio_chunk)
        if rms < self.rms_threshold:
            return False  # Claramente silêncio
        
        # 2. Segundo filtro: VAD
        try:
            if self.webrtc_vad:
                vad_result = self._webrtc_vad_check(audio_chunk)
            else:
                vad_result = self.vad.is_speech(audio_chunk)
            
            # 3. Telemetria de falsos positivos
            if rms >= self.rms_threshold and not vad_result:
                self.vad_false_positives += 1
            
            return vad_result if vad_result is not None else True
        
        except Exception as e:
            print(f"⚠️ VAD falhou: {e}, usando RMS")
            return True  # RMS já passou, assume fala
    
    def _webrtc_vad_check(self, audio_chunk: bytes) -> bool:
        """
        Verifica usando WebRTC VAD
        """
        frame_duration_ms = 30
        sample_rate = 16000
        frame_size = int(sample_rate * frame_duration_ms / 1000) * 2
        
        for i in range(0, len(audio_chunk), frame_size):
            frame = audio_chunk[i:i+frame_size]
            if len(frame) == frame_size:
                try:
                    if self.webrtc_vad.is_speech(frame, sample_rate):
                        return True
                except Exception:
                    continue
        return False
    
    def _get_rms(self, audio_chunk: bytes) -> int:
        """
        Calcula RMS do audio
        """
        try:
            return audioop.rms(audio_chunk, 2)
        except Exception:
            return 0
    
    def _rms_detection(self, audio_chunk: bytes) -> bool:
        """
        Detecção por RMS (fallback)
        """
        return self._get_rms(audio_chunk) > self.rms_threshold
    
    def get_false_positive_count(self) -> int:
        """
        Retorna contagem de falsos positivos para telemetria
        """
        return self.vad_false_positives
