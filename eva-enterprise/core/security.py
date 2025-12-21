"""
Security Manager - Eva Enterprise
Gerencia autenticação, autorização e segurança
"""
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from functools import wraps


class SecurityManager:
    """Gerencia autenticação e autorização."""
    
    def __init__(self, secret_key: str, token_expiry_hours: int = 24):
        """
        Args:
            secret_key: Chave secreta para JWT
            token_expiry_hours: Tempo de expiração do token em horas
        """
        self.secret_key = secret_key
        self.token_expiry = timedelta(hours=token_expiry_hours)
        self.refresh_token_expiry = timedelta(days=7)
        self.algorithm = 'HS256'
    
    def generate_token(self, user_id: int, role: str, extra_claims: dict = None) -> str:
        """
        Gera JWT token para autenticação.
        
        Args:
            user_id: ID do usuário
            role: Role do usuário (admin, operator, family, etc)
            extra_claims: Claims adicionais opcionais
            
        Returns:
            Token JWT codificado
        """
        payload = {
            'user_id': user_id,
            'role': role,
            'exp': datetime.utcnow() + self.token_expiry,
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        
        if extra_claims:
            payload.update(extra_claims)
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def generate_refresh_token(self, user_id: int) -> str:
        """Gera refresh token de longa duração."""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + self.refresh_token_expiry,
            'iat': datetime.utcnow(),
            'type': 'refresh',
            'jti': secrets.token_hex(16)  # Unique ID para revogação
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[dict]:
        """
        Verifica e decodifica JWT token.
        
        Args:
            token: Token JWT
            
        Returns:
            Payload decodificado ou None se inválido
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            print("⚠️ [SECURITY] Token expirado")
            return None
        except jwt.InvalidTokenError as e:
            print(f"⚠️ [SECURITY] Token inválido: {e}")
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        Gera novo access token usando refresh token.
        
        Args:
            refresh_token: Refresh token válido
            
        Returns:
            Novo access token ou None se refresh inválido
        """
        payload = self.verify_token(refresh_token)
        
        if not payload:
            return None
        
        if payload.get('type') != 'refresh':
            print("⚠️ [SECURITY] Token não é refresh token")
            return None
        
        # Buscar role do usuário (em produção, buscar do banco)
        # Por enquanto, retorna token básico
        return self.generate_token(payload['user_id'], 'user')
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash de senha com salt usando PBKDF2.
        
        Args:
            password: Senha em texto plano
            
        Returns:
            Hash no formato "salt$hash"
        """
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256', 
            password.encode(), 
            salt.encode(), 
            100000  # Iterações
        )
        return f"{salt}${pwd_hash.hex()}"
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        Verifica senha contra hash.
        
        Args:
            password: Senha em texto plano
            hashed: Hash armazenado
            
        Returns:
            True se senha correta
        """
        try:
            salt, pwd_hash = hashed.split('$')
            new_hash = hashlib.pbkdf2_hmac(
                'sha256', 
                password.encode(), 
                salt.encode(), 
                100000
            )
            return secrets.compare_digest(new_hash.hex(), pwd_hash)
        except Exception:
            return False
    
    @staticmethod
    def generate_api_key() -> str:
        """Gera API key segura."""
        return f"eva_{secrets.token_urlsafe(32)}"


class RoleManager:
    """Gerencia roles e permissões."""
    
    # Definição de permissões por role
    PERMISSIONS = {
        'admin': ['*'],  # Acesso total
        'operator': [
            'view:calls',
            'view:idosos',
            'view:agendamentos',
            'create:agendamentos',
            'update:agendamentos',
            'view:alerts',
            'resolve:alerts'
        ],
        'family': [
            'view:idoso_own',
            'view:calls_own',
            'view:alerts_own',
            'update:idoso_own'
        ],
        'readonly': [
            'view:calls',
            'view:idosos',
            'view:agendamentos',
            'view:alerts'
        ]
    }
    
    @classmethod
    def has_permission(cls, role: str, permission: str) -> bool:
        """
        Verifica se role tem permissão.
        
        Args:
            role: Role do usuário
            permission: Permissão requerida (ex: 'view:calls')
            
        Returns:
            True se tem permissão
        """
        permissions = cls.PERMISSIONS.get(role, [])
        
        # Admin tem acesso total
        if '*' in permissions:
            return True
        
        # Verifica permissão exata
        if permission in permissions:
            return True
        
        # Verifica permissão wildcard (ex: 'view:*')
        action, resource = permission.split(':') if ':' in permission else (permission, '*')
        if f'{action}:*' in permissions:
            return True
        
        return False
    
    @classmethod
    def get_permissions(cls, role: str) -> List[str]:
        """Retorna lista de permissões para role."""
        return cls.PERMISSIONS.get(role, [])


def require_auth(required_permission: str = None):
    """
    Decorator para proteger endpoints com autenticação.
    
    Args:
        required_permission: Permissão necessária (opcional)
    
    Usage:
        @require_auth('view:calls')
        async def list_calls(request):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Em FastAPI, request vem como argumento
            request = kwargs.get('request') or (args[0] if args else None)
            
            if not request:
                raise ValueError("Request não encontrado")
            
            # Extrai token do header
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                from fastapi import HTTPException
                raise HTTPException(status_code=401, detail="Token não fornecido")
            
            token = auth_header.replace('Bearer ', '')
            
            # Verifica token (assume SecurityManager global)
            # Em produção, usar dependency injection
            from ..config.settings import settings
            security = SecurityManager(settings.JWT_SECRET_KEY)
            payload = security.verify_token(token)
            
            if not payload:
                from fastapi import HTTPException
                raise HTTPException(status_code=401, detail="Token inválido")
            
            # Verifica permissão se especificada
            if required_permission:
                role = payload.get('role', '')
                if not RoleManager.has_permission(role, required_permission):
                    from fastapi import HTTPException
                    raise HTTPException(status_code=403, detail="Permissão negada")
            
            # Adiciona user ao request state
            request.state.user = payload
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


class RateLimiter:
    """Rate limiting simples em memória."""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = timedelta(seconds=window_seconds)
        self.requests: Dict[str, List[datetime]] = {}
    
    def is_allowed(self, key: str) -> bool:
        """
        Verifica se requisição é permitida.
        
        Args:
            key: Identificador (IP, user_id, etc)
            
        Returns:
            True se dentro do limite
        """
        now = datetime.utcnow()
        
        # Limpa requisições antigas
        if key in self.requests:
            self.requests[key] = [
                t for t in self.requests[key] 
                if now - t < self.window
            ]
        else:
            self.requests[key] = []
        
        # Verifica limite
        if len(self.requests[key]) >= self.max_requests:
            return False
        
        # Registra requisição
        self.requests[key].append(now)
        return True
    
    def get_remaining(self, key: str) -> int:
        """Retorna requisições restantes."""
        now = datetime.utcnow()
        
        if key not in self.requests:
            return self.max_requests
        
        valid_requests = [t for t in self.requests[key] if now - t < self.window]
        return max(0, self.max_requests - len(valid_requests))


# Singleton para uso global
_security_manager: Optional[SecurityManager] = None
_rate_limiter: Optional[RateLimiter] = None


def get_security_manager() -> SecurityManager:
    """Retorna instância singleton do SecurityManager."""
    global _security_manager
    if _security_manager is None:
        from ..config.settings import settings
        secret_key = getattr(settings, 'JWT_SECRET_KEY', secrets.token_hex(32))
        _security_manager = SecurityManager(secret_key)
    return _security_manager


def get_rate_limiter() -> RateLimiter:
    """Retorna instância singleton do RateLimiter."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter
