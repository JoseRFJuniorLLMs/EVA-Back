import hashlib
import re
from typing import Optional

class WiseReferenceGenerator:
    """
    Gerador de códigos de referência únicos para Wise.
    
    Format: EVA-{COMPONENT}-{USER_ID}-{CHECKSUM}
    Example: EVA-USER-12345-A3B2
    """
    
    PREFIX = "EVA"
    
    @staticmethod
    def generate(user_id: int, component: str = "USER") -> str:
        """
        Gera código de referência único.
        
        Args:
            user_id: ID do usuário
            component: Tipo (USER, ORG, RENEWAL)
        
        Returns:
            Código formatado (ex: EVA-USER-12345-A3B2)
        """
        # Validar component
        valid_components = ["USER", "ORG", "RENEWAL"]
        if component not in valid_components:
            raise ValueError(f"Component must be one of: {valid_components}")
        
        # Criar base
        base = f"{WiseReferenceGenerator.PREFIX}-{component}-{user_id}"
        
        # Calcular checksum (CRC32 truncado)
        checksum = hashlib.md5(base.encode()).hexdigest()[:4].upper()
        
        # Retornar código completo
        return f"{base}-{checksum}"
    
    @staticmethod
    def validate(reference: str) -> bool:
        """
        Valida formato do código.
        
        Args:
            reference: Código a validar
        
        Returns:
            True se válido
        """
        pattern = r"^EVA-(USER|ORG|RENEWAL)-\d+-[A-F0-9]{4}$"
        return bool(re.match(pattern, reference))
    
    @staticmethod
    def extract_user_id(reference: str) -> Optional[int]:
        """
        Extrai user_id do código.
        
        Args:
            reference: Código completo
        
        Returns:
            User ID ou None se inválido
        """
        if not WiseReferenceGenerator.validate(reference):
            return None
        
        parts = reference.split("-")
        try:
            return int(parts[2])
        except (IndexError, ValueError):
            return None
    
    @staticmethod
    def verify_checksum(reference: str) -> bool:
        """
        Verifica integridade do checksum.
        
        Args:
            reference: Código completo
        
        Returns:
            True se checksum válido
        """
        if not WiseReferenceGenerator.validate(reference):
            return False
        
        parts = reference.split("-")
        base = "-".join(parts[:-1])  # Tudo menos checksum
        provided_checksum = parts[-1]
        
        # Recalcular checksum
        expected_checksum = hashlib.md5(base.encode()).hexdigest()[:4].upper()
        
        return provided_checksum == expected_checksum
