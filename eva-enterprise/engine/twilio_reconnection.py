"""
Twilio Stream Reconnection Manager
Detecta quedas de conexão e gerencia tentativas de reconexão automática
"""
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Callable


class TwilioStreamReconnection:
    """
    Detecta quedas de stream do Twilio e tenta reconectar automaticamente.
    
    Funcionalidades:
    - Watchdog que monitora recebimento de pacotes
    - Detecção de timeout (sem pacotes por X segundos)
    - Tentativas automáticas de reconexão
    - Callbacks para notificar eventos
    """
    
    def __init__(
        self, 
        max_reconnection_attempts: int = 5,
        reconnection_timeout: float = 30.0,
        packet_timeout: float = 10.0
    ):
        """
        Args:
            max_reconnection_attempts: Máximo de tentativas de reconexão
            reconnection_timeout: Timeout total para reconexão (segundos)
            packet_timeout: Tempo sem pacotes para considerar desconectado
        """
        self.max_attempts = max_reconnection_attempts
        self.timeout = reconnection_timeout
        self.packet_timeout = packet_timeout
        
        # Estado
        self.last_packet_time = datetime.utcnow()
        self.is_connected = False
        self.reconnection_attempts = 0
        self.connection_start_time = None
        
        # Tasks
        self.watchdog_task: Optional[asyncio.Task] = None
        
        # Callbacks
        self.on_disconnect: Optional[Callable] = None
        self.on_reconnect: Optional[Callable] = None
        self.on_max_attempts_reached: Optional[Callable] = None
    
    def mark_connected(self):
        """Marca como conectado (chamado no início da conexão)"""
        self.is_connected = True
        self.connection_start_time = datetime.utcnow()
        self.reconnection_attempts = 0
        self.last_packet_time = datetime.utcnow()
        print("✓ [TWILIO] Stream conectado")
    
    def mark_packet_received(self):
        """Chamado quando recebe pacote do Twilio"""
        self.last_packet_time = datetime.utcnow()
        self.is_connected = True
    
    def mark_disconnected(self):
        """Marca como desconectado"""
        self.is_connected = False
        print("✗ [TWILIO] Stream desconectado")
    
    async def start_watchdog(self, on_timeout_callback: Callable = None):
        """
        Inicia watchdog que detecta timeout.
        
        Args:
            on_timeout_callback: Callback assíncrono chamado em timeout
        """
        self.watchdog_task = asyncio.create_task(
            self._watchdog_loop(on_timeout_callback)
        )
        print("🐕 [WATCHDOG] Monitoramento de stream iniciado")
    
    async def _watchdog_loop(self, callback: Callable = None):
        """Loop que verifica se stream está ativo."""
        try:
            while True:
                await asyncio.sleep(5)  # Verifica a cada 5 segundos
                
                if not self.is_connected:
                    continue
                
                time_since_packet = (datetime.utcnow() - self.last_packet_time).total_seconds()
                
                if time_since_packet > self.packet_timeout:
                    print(f"🚨 [TWILIO] Stream timeout! ({time_since_packet:.1f}s sem pacotes)")
                    self.mark_disconnected()
                    
                    # Notifica callback de desconexão
                    if self.on_disconnect:
                        try:
                            await self.on_disconnect()
                        except Exception as e:
                            print(f"⚠️ [WATCHDOG] Erro no callback de desconexão: {e}")
                    
                    # Tenta reconectar
                    if self.reconnection_attempts < self.max_attempts:
                        self.reconnection_attempts += 1
                        print(f"🔄 [TWILIO] Tentativa {self.reconnection_attempts}/{self.max_attempts}")
                        
                        try:
                            if callback:
                                await asyncio.wait_for(callback(), timeout=self.timeout)
                                
                                # Se reconectou com sucesso
                                if self.on_reconnect:
                                    await self.on_reconnect()
                        except asyncio.TimeoutError:
                            print(f"✗ [TWILIO] Timeout na reconexão ({self.timeout}s)")
                        except Exception as e:
                            print(f"✗ [TWILIO] Falha na reconexão: {e}")
                    else:
                        print(f"✗ [TWILIO] Esgotadas tentativas de reconexão")
                        
                        # Notifica que esgotou tentativas
                        if self.on_max_attempts_reached:
                            try:
                                await self.on_max_attempts_reached()
                            except Exception as e:
                                print(f"⚠️ [WATCHDOG] Erro no callback de max attempts: {e}")
                        break
        
        except asyncio.CancelledError:
            print("🐕 [WATCHDOG] Monitoramento cancelado")
        except Exception as e:
            print(f"✗ [WATCHDOG] Erro no watchdog: {e}")
    
    def stop_watchdog(self):
        """Para o watchdog"""
        if self.watchdog_task:
            self.watchdog_task.cancel()
            self.watchdog_task = None
            print("🐕 [WATCHDOG] Monitoramento parado")
    
    def get_connection_stats(self) -> dict:
        """Retorna estatísticas da conexão"""
        uptime = None
        if self.connection_start_time and self.is_connected:
            uptime = (datetime.utcnow() - self.connection_start_time).total_seconds()
        
        return {
            'is_connected': self.is_connected,
            'reconnection_attempts': self.reconnection_attempts,
            'last_packet_ago_seconds': (datetime.utcnow() - self.last_packet_time).total_seconds(),
            'uptime_seconds': uptime
        }
    
    async def wait_for_reconnection(self, timeout: float = None) -> bool:
        """
        Aguarda reconexão (útil para chamar após detectar queda).
        
        Args:
            timeout: Tempo máximo de espera (usa self.timeout se None)
            
        Returns:
            True se reconectou, False se timeout
        """
        timeout = timeout or self.timeout
        start = datetime.utcnow()
        
        while (datetime.utcnow() - start).total_seconds() < timeout:
            if self.is_connected:
                return True
            await asyncio.sleep(0.5)
        
        return False


class ConnectionHealthMonitor:
    """
    Monitor de saúde da conexão com métricas.
    """
    
    def __init__(self):
        self.packets_received = 0
        self.packets_lost = 0
        self.connection_drops = 0
        self.total_reconnections = 0
        self.latency_samples = []
        self.start_time = datetime.utcnow()
    
    def record_packet(self, latency_ms: float = None):
        """Registra pacote recebido"""
        self.packets_received += 1
        if latency_ms:
            self.latency_samples.append(latency_ms)
            # Mantém apenas últimas 100 amostras
            if len(self.latency_samples) > 100:
                self.latency_samples.pop(0)
    
    def record_connection_drop(self):
        """Registra queda de conexão"""
        self.connection_drops += 1
    
    def record_reconnection(self):
        """Registra reconexão bem-sucedida"""
        self.total_reconnections += 1
    
    def get_metrics(self) -> dict:
        """Retorna métricas de saúde"""
        avg_latency = None
        if self.latency_samples:
            avg_latency = sum(self.latency_samples) / len(self.latency_samples)
        
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        
        return {
            'uptime_seconds': uptime,
            'packets_received': self.packets_received,
            'packets_lost': self.packets_lost,
            'connection_drops': self.connection_drops,
            'reconnections': self.total_reconnections,
            'avg_latency_ms': avg_latency,
            'packet_rate_per_second': self.packets_received / max(uptime, 1)
        }
