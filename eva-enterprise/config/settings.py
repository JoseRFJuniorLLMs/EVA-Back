import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PORT = int(os.getenv("PORT", "8080"))
    SERVICE_DOMAIN = os.getenv("SERVICE_DOMAIN")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
    
    MODEL_ID = "gemini-2.5-flash-native-audio-preview-12-2025"

    # Configurações adicionais
    DATABASE_URL = os.getenv("DATABASE_URL")
    MAX_CONCURRENT_CALLS = int(os.getenv("MAX_CONCURRENT_CALLS", "10"))
    CIRCUIT_BREAKER_THRESHOLD = int(os.getenv("CIRCUIT_BREAKER_THRESHOLD", "5"))
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

settings = Settings()


class DynamicConfig:
    """Configurações dinâmicas carregadas do banco de dados com cache."""
    _cache = {}  # Cache em memória para evitar DB hit a cada chamada
    _cache_ttl = 60  # Recarrega configs a cada 60s
    _cache_timestamps = {}  # Timestamps de quando cada key foi cacheada
    
    def _is_expired(self, key: str) -> bool:
        """Verifica se o cache da key expirou."""
        import time
        if key not in self._cache_timestamps:
            return True
        return (time.time() - self._cache_timestamps[key]) > self._cache_ttl
    
    async def get(self, key: str, default=None):
        """Busca configuração do banco de dados."""
        # TODO: Implementar busca real no banco (tabela configuracoes_sistema)
        return default
    
    async def get_cached(self, key: str, default=None):
        """Usa cache com TTL para não sobrecarregar banco."""
        import time
        if key not in self._cache or self._is_expired(key):
            self._cache[key] = await self.get(key, default)
            self._cache_timestamps[key] = time.time()
        return self._cache[key]


dynamic_config = DynamicConfig()
