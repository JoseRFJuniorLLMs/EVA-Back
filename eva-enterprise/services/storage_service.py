"""
Google Cloud Storage Service
Serviço para upload e gerenciamento de comprovantes de pagamento
"""
from google.cloud import storage
from google.oauth2 import service_account
from typing import Optional
from uuid import uuid4
from datetime import datetime, timedelta
import os
import logging

logger = logging.getLogger(__name__)


class StorageService:
    """Service para Google Cloud Storage"""
    
    def __init__(self):
        """Inicializa GCS client"""
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        project_id = os.getenv("GCP_PROJECT_ID")
        self.bucket_name = os.getenv("GCS_BUCKET_NAME", "eva-receipts")
        
        if credentials_path and os.path.exists(credentials_path):
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path
            )
            self.client = storage.Client(
                project=project_id,
                credentials=credentials
            )
        else:
            # Usar credenciais padrão (útil em produção no GCP)
            self.client = storage.Client(project=project_id)
        
        self.bucket = self.client.bucket(self.bucket_name)
    
    async def upload_receipt(
        self,
        file_content: bytes,
        file_name: str,
        content_type: str,
        user_id: int,
        transaction_id: int
    ) -> dict:
        """
        Upload de comprovante para GCS.
        
        Args:
            file_content: Conteúdo do arquivo em bytes
            file_name: Nome original do arquivo
            content_type: MIME type
            user_id: ID do usuário
            transaction_id: ID da transação
        
        Returns:
            {
                "url": "https://storage.googleapis.com/...",
                "blob_name": "receipts/123/456_xxx.pdf",
                "size": 123456
            }
        """
        # Gerar nome único
        file_ext = file_name.split(".")[-1] if "." in file_name else "pdf"
        blob_name = f"receipts/{user_id}/{transaction_id}_{uuid4().hex}.{file_ext}"
        
        # Upload
        blob = self.bucket.blob(blob_name)
        blob.upload_from_string(
            file_content,
            content_type=content_type
        )
        
        # Metadata
        blob.metadata = {
            "user_id": str(user_id),
            "transaction_id": str(transaction_id),
            "uploaded_at": datetime.utcnow().isoformat(),
            "original_name": file_name
        }
        blob.patch()
        
        url = f"https://storage.googleapis.com/{self.bucket_name}/{blob_name}"
        
        logger.info(
            f"Receipt uploaded",
            extra={
                "user_id": user_id,
                "transaction_id": transaction_id,
                "blob_name": blob_name,
                "size": blob.size
            }
        )
        
        return {
            "url": url,
            "blob_name": blob_name,
            "size": blob.size
        }
    
    def generate_signed_url(
        self,
        blob_name: str,
        expiration_minutes: int = 60
    ) -> str:
        """
        Gera URL assinada com expiração.
        
        Args:
            blob_name: Nome do blob
            expiration_minutes: Tempo de expiração em minutos
        
        Returns:
            URL assinada
        """
        blob = self.bucket.blob(blob_name)
        
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=expiration_minutes),
            method="GET"
        )
        
        return url
    
    async def delete_receipt(self, blob_name: str) -> bool:
        """
        Remove arquivo do GCS.
        
        Args:
            blob_name: Nome do blob
        
        Returns:
            True se deletado com sucesso
        """
        blob = self.bucket.blob(blob_name)
        
        if not blob.exists():
            return False
        
        blob.delete()
        
        logger.info(f"Receipt deleted", extra={"blob_name": blob_name})
        
        return True
    
    async def list_user_receipts(
        self,
        user_id: int,
        max_results: int = 50
    ) -> list:
        """
        Lista comprovantes de um usuário.
        
        Args:
            user_id: ID do usuário
            max_results: Máximo de resultados
        
        Returns:
            Lista de arquivos
        """
        prefix = f"receipts/{user_id}/"
        
        blobs = self.bucket.list_blobs(
            prefix=prefix,
            max_results=max_results
        )
        
        files = []
        for blob in blobs:
            files.append({
                "name": blob.name,
                "size": blob.size,
                "created": blob.time_created.isoformat() if blob.time_created else None,
                "url": f"https://storage.googleapis.com/{self.bucket_name}/{blob.name}",
                "metadata": blob.metadata or {}
            })
        
        return files
