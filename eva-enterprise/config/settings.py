import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Configurações da aplicação"""
    # Server
    PORT = int(os.getenv("PORT", "8080"))
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # API Limits
    MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "100"))
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


settings = Settings()


class DynamicConfig:
    """Configurações dinâmicas carregadas do banco de dados com cache."""
    _cache = {}
    _cache_ttl = 60
    _cache_timestamps = {}
    
    def _is_expired(self, key: str) -> bool:
        """Verifica se o cache da key expirou."""
        import time
        if key not in self._cache_timestamps:
            return True
        return (time.time() - self._cache_timestamps[key]) > self._cache_ttl
    
    async def get(self, key: str, default=None):
        """
        Busca configuração do banco de dados.
        
        Args:
            key: Chave da configuração
            default: Valor padrão caso não encontre
            
        Returns:
            Valor da configuração ou default
        """
        # TODO: Implementar busca real no banco (tabela configuracoes_sistema)
        return default
    
    async def get_cached(self, key: str, default=None):
        """
        Usa cache com TTL para não sobrecarregar banco.
        
        Args:
            key: Chave da configuração
            default: Valor padrão caso não encontre
            
        Returns:
            Valor da configuração (cacheado) ou default
        """
        import time
        if key not in self._cache or self._is_expired(key):
            self._cache[key] = await self.get(key, default)
            self._cache_timestamps[key] = time.time()
        return self._cache[key]
    
    def clear_cache(self, key: str = None):
        """
        Limpa cache de uma key específica ou todo o cache.
        
        Args:
            key: Chave específica para limpar (None limpa tudo)
        """
        if key:
            self._cache.pop(key, None)
            self._cache_timestamps.pop(key, None)
        else:
            self._cache.clear()
            self._cache_timestamps.clear()


dynamic_config = DynamicConfig()