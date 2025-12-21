"""
Monitoring Dashboard - Eva Enterprise
Endpoints para health check, métricas e monitoramento em tempo real
"""
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional
from fastapi import APIRouter
import asyncio
import time

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])


# ================================================================
# CIRCUIT BREAKER
# ================================================================

class CircuitState(Enum):
    """Estados do circuit breaker."""
    CLOSED = "closed"      # Normal, permitindo requisições
    OPEN = "open"          # Aberto, bloqueando requisições
    HALF_OPEN = "half_open"  # Testando se pode fechar


class CircuitBreaker:
    """
    Circuit Breaker Pattern para proteção de serviços externos.
    
    Evita cascata de falhas quando um serviço externo está fora.
    """
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        half_open_max_calls: int = 3
    ):
        """
        Args:
            name: Nome do circuit breaker
            failure_threshold: Falhas consecutivas para abrir
            recovery_timeout: Segundos antes de tentar half-open
            half_open_max_calls: Chamadas permitidas em half-open
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.successes = 0
        self.last_failure_time: Optional[float] = None
        self.half_open_calls = 0
    
    def can_execute(self) -> bool:
        """Verifica se pode executar chamada."""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            # Verifica se timeout passou para tentar half-open
            if self.last_failure_time:
                elapsed = time.time() - self.last_failure_time
                if elapsed >= self.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_calls = 0
                    print(f"🔄 [CIRCUIT:{self.name}] Tentando half-open após {elapsed:.1f}s")
                    return True
            return False
        
        if self.state == CircuitState.HALF_OPEN:
            return self.half_open_calls < self.half_open_max_calls
        
        return False
    
    def record_success(self):
        """Registra sucesso."""
        if self.state == CircuitState.HALF_OPEN:
            self.successes += 1
            self.half_open_calls += 1
            
            # Se conseguiu X sucessos, fecha o circuito
            if self.successes >= self.half_open_max_calls:
                self.state = CircuitState.CLOSED
                self.failures = 0
                self.successes = 0
                print(f"✓ [CIRCUIT:{self.name}] Fechado (recuperado)")
        else:
            self.failures = 0
    
    def record_failure(self):
        """Registra falha."""
        self.failures += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            # Falhou em half-open, volta a abrir
            self.state = CircuitState.OPEN
            self.successes = 0
            print(f"✗ [CIRCUIT:{self.name}] Reaberto (falha em half-open)")
        
        elif self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
            print(f"⚠️ [CIRCUIT:{self.name}] Aberto após {self.failures} falhas")
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status do circuit breaker."""
        return {
            'name': self.name,
            'state': self.state.value,
            'failures': self.failures,
            'last_failure': self.last_failure_time,
            'recovery_in': max(0, self.recovery_timeout - (time.time() - (self.last_failure_time or 0)))
                if self.state == CircuitState.OPEN else None
        }


# Circuit Breakers globais
GEMINI_CIRCUIT_BREAKER = CircuitBreaker("gemini", failure_threshold=3, recovery_timeout=60)
TWILIO_CIRCUIT_BREAKER = CircuitBreaker("twilio", failure_threshold=5, recovery_timeout=30)


# ================================================================
# MÉTRICAS EM TEMPO REAL
# ================================================================

class MetricsCollector:
    """Coleta métricas do sistema."""
    
    def __init__(self):
        self.start_time = datetime.utcnow()
        self.metrics = {
            'calls_total': 0,
            'calls_successful': 0,
            'calls_failed': 0,
            'calls_in_progress': 0,
            'avg_call_duration': 0,
            'total_call_duration': 0,
            'gemini_requests': 0,
            'gemini_errors': 0,
            'twilio_requests': 0,
            'twilio_errors': 0,
            'vad_false_positives': 0,
            'alerts_sent': 0
        }
        self._lock = asyncio.Lock()
    
    async def increment(self, metric: str, value: int = 1):
        """Incrementa métrica."""
        async with self._lock:
            if metric in self.metrics:
                self.metrics[metric] += value
    
    async def set(self, metric: str, value: Any):
        """Define valor de métrica."""
        async with self._lock:
            self.metrics[metric] = value
    
    async def record_call_completed(self, duration_seconds: float, success: bool):
        """Registra chamada completada."""
        async with self._lock:
            self.metrics['calls_total'] += 1
            self.metrics['calls_in_progress'] = max(0, self.metrics['calls_in_progress'] - 1)
            
            if success:
                self.metrics['calls_successful'] += 1
            else:
                self.metrics['calls_failed'] += 1
            
            # Atualiza duração média
            self.metrics['total_call_duration'] += duration_seconds
            self.metrics['avg_call_duration'] = (
                self.metrics['total_call_duration'] / self.metrics['calls_total']
            )
    
    def get_all(self) -> Dict[str, Any]:
        """Retorna todas as métricas."""
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        
        return {
            **self.metrics,
            'uptime_seconds': uptime,
            'calls_per_hour': self.metrics['calls_total'] / (uptime / 3600) if uptime > 0 else 0,
            'success_rate': (
                self.metrics['calls_successful'] / self.metrics['calls_total'] * 100
                if self.metrics['calls_total'] > 0 else 0
            )
        }


# Singleton global
metrics_collector = MetricsCollector()


# ================================================================
# ENDPOINTS
# ================================================================

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint.
    
    Verifica status de componentes críticos.
    """
    gemini_healthy = GEMINI_CIRCUIT_BREAKER.state != CircuitState.OPEN
    twilio_healthy = TWILIO_CIRCUIT_BREAKER.state != CircuitState.OPEN
    
    overall_status = "healthy" if (gemini_healthy and twilio_healthy) else "degraded"
    
    return {
        'status': overall_status,
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.0.0',
        'components': {
            'gemini': 'healthy' if gemini_healthy else 'unhealthy',
            'twilio': 'healthy' if twilio_healthy else 'unhealthy',
            'database': 'healthy'  # TODO: Verificar conexão
        }
    }


@router.get("/health/live")
async def liveness_probe() -> Dict[str, str]:
    """Kubernetes liveness probe."""
    return {'status': 'alive'}


@router.get("/health/ready")
async def readiness_probe() -> Dict[str, Any]:
    """Kubernetes readiness probe."""
    # Verifica se sistema está pronto para receber tráfego
    gemini_ready = GEMINI_CIRCUIT_BREAKER.state != CircuitState.OPEN
    twilio_ready = TWILIO_CIRCUIT_BREAKER.state != CircuitState.OPEN
    
    if gemini_ready and twilio_ready:
        return {'status': 'ready'}
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Service not ready")


@router.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """
    Retorna métricas do sistema.
    
    Inclui métricas de chamadas, Gemini, Twilio e circuit breakers.
    """
    all_metrics = metrics_collector.get_all()
    
    return {
        'calls': {
            'total': all_metrics['calls_total'],
            'successful': all_metrics['calls_successful'],
            'failed': all_metrics['calls_failed'],
            'in_progress': all_metrics['calls_in_progress'],
            'avg_duration_seconds': round(all_metrics['avg_call_duration'], 2),
            'per_hour': round(all_metrics['calls_per_hour'], 2),
            'success_rate_pct': round(all_metrics['success_rate'], 2)
        },
        'gemini': {
            'requests': all_metrics['gemini_requests'],
            'errors': all_metrics['gemini_errors'],
            'circuit_breaker': GEMINI_CIRCUIT_BREAKER.get_status()
        },
        'twilio': {
            'requests': all_metrics['twilio_requests'],
            'errors': all_metrics['twilio_errors'],
            'circuit_breaker': TWILIO_CIRCUIT_BREAKER.get_status()
        },
        'audio': {
            'vad_false_positives': all_metrics['vad_false_positives']
        },
        'alerts': {
            'sent': all_metrics['alerts_sent']
        },
        'system': {
            'uptime_seconds': round(all_metrics['uptime_seconds'], 0)
        }
    }


@router.get("/metrics/prometheus")
async def get_prometheus_metrics() -> str:
    """
    Métricas em formato Prometheus.
    
    Para integração com stack de observabilidade.
    """
    all_metrics = metrics_collector.get_all()
    
    lines = [
        "# HELP eva_calls_total Total de chamadas realizadas",
        "# TYPE eva_calls_total counter",
        f"eva_calls_total {all_metrics['calls_total']}",
        "",
        "# HELP eva_calls_successful Chamadas bem-sucedidas",
        "# TYPE eva_calls_successful counter",
        f"eva_calls_successful {all_metrics['calls_successful']}",
        "",
        "# HELP eva_calls_failed Chamadas com falha",
        "# TYPE eva_calls_failed counter",
        f"eva_calls_failed {all_metrics['calls_failed']}",
        "",
        "# HELP eva_calls_in_progress Chamadas em andamento",
        "# TYPE eva_calls_in_progress gauge",
        f"eva_calls_in_progress {all_metrics['calls_in_progress']}",
        "",
        "# HELP eva_call_duration_avg Duração média das chamadas",
        "# TYPE eva_call_duration_avg gauge",
        f"eva_call_duration_avg {all_metrics['avg_call_duration']:.2f}",
        "",
        "# HELP eva_gemini_requests Total de requisições ao Gemini",
        "# TYPE eva_gemini_requests counter",
        f"eva_gemini_requests {all_metrics['gemini_requests']}",
        "",
        "# HELP eva_uptime_seconds Tempo de atividade em segundos",
        "# TYPE eva_uptime_seconds gauge",
        f"eva_uptime_seconds {all_metrics['uptime_seconds']:.0f}",
    ]
    
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse("\n".join(lines), media_type="text/plain")


@router.get("/calls/active")
async def get_active_calls() -> Dict[str, Any]:
    """Retorna lista de chamadas ativas."""
    # TODO: Implementar tracking de chamadas ativas
    return {
        'count': metrics_collector.metrics['calls_in_progress'],
        'calls': []  # Implementar lista de chamadas
    }


@router.get("/circuit-breakers")
async def get_circuit_breakers() -> Dict[str, Any]:
    """Retorna status de todos os circuit breakers."""
    return {
        'gemini': GEMINI_CIRCUIT_BREAKER.get_status(),
        'twilio': TWILIO_CIRCUIT_BREAKER.get_status()
    }


@router.post("/circuit-breakers/{name}/reset")
async def reset_circuit_breaker(name: str) -> Dict[str, str]:
    """Reseta um circuit breaker manualmente."""
    if name == 'gemini':
        GEMINI_CIRCUIT_BREAKER.state = CircuitState.CLOSED
        GEMINI_CIRCUIT_BREAKER.failures = 0
        return {'status': 'reset', 'name': 'gemini'}
    
    elif name == 'twilio':
        TWILIO_CIRCUIT_BREAKER.state = CircuitState.CLOSED
        TWILIO_CIRCUIT_BREAKER.failures = 0
        return {'status': 'reset', 'name': 'twilio'}
    
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail=f"Circuit breaker '{name}' não encontrado")
