import firebase_admin
from firebase_admin import credentials, messaging
import os
import logging

# Configuração de Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NotificationService, cls).__new__(cls)
            cls._instance.initialize_firebase()
        return cls._instance

    def initialize_firebase(self):
        try:
            # Caminho para o arquivo de credenciais (ajuste conforme necessário)
            cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-adminsdk.json")
            
            if not firebase_admin._apps:
                if os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                    logger.info("Firebase Admin SDK inicializado com sucesso.")
                else:
                    logger.warning(f"Arquivo de credenciais Firebase não encontrado em: {cred_path}. Push notifications desativadas.")
        except Exception as e:
            logger.error(f"Erro ao inicializar Firebase: {e}")

    def send_push_notification(self, token: str, title: str, body: str, data: dict = None):
        """Dispara uma notificação push para um dispositivo específico."""
        if not firebase_admin._apps:
            logger.warning("Tentativa de envio de push sem Firebase inicializado.")
            return False

        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                token=token,
            )
            response = messaging.send(message)
            logger.info(f"Push enviado com sucesso: {response}")
            return True
        except Exception as e:
            logger.error(f"Falha ao enviar push: {e}")
            return False

    def send_multicast_notification(self, tokens: list, title: str, body: str, data: dict = None):
        """Envia para múltiplos dispositivos."""
        if not tokens or not firebase_admin._apps:
            return False
            
        try:
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                tokens=tokens,
            )
            response = messaging.send_multicast(message)
            logger.info(f"Multicast enviado. Sucessos: {response.success_count}, Falhas: {response.failure_count}")
            return True
        except Exception as e:
            logger.error(f"Falha no multicast: {e}")
            return False
