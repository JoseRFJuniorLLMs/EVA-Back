"""
Notification Tasks
==================
Tasks Celery para envio assincrono de notificacoes.

Tipos de notificacao:
- Push notifications (Firebase)
- Email (SMTP/SendGrid)
- SMS (Twilio) - futuro
"""
import logging
from typing import Dict, List, Optional
from celery import shared_task

from database.connection_sync import get_sync_db
from database.models import Usuario as User, Cuidador
from sqlalchemy import select

logger = logging.getLogger(__name__)


def get_firebase_service():
    """Lazy import do NotificationService para evitar import circular."""
    from services.notification_service import NotificationService
    return NotificationService()


# ==========================================
# PUSH NOTIFICATIONS
# ==========================================

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
    name="tasks.notification_tasks.send_push_notification"
)
def send_push_notification(
    self,
    device_token: str,
    title: str,
    body: str,
    data: Optional[Dict] = None
) -> Dict:
    """
    Envia notificacao push para um dispositivo.

    Args:
        device_token: Token FCM do dispositivo
        title: Titulo da notificacao
        body: Corpo da mensagem
        data: Dados extras (opcional)

    Returns:
        dict: Status do envio
    """
    logger.info(f"Sending push notification: {title}")

    try:
        firebase = get_firebase_service()
        success = firebase.send_push_notification(
            token=device_token,
            title=title,
            body=body,
            data=data or {}
        )

        if success:
            logger.info(f"Push notification sent successfully to {device_token[:20]}...")
            return {"status": "sent", "token": device_token[:20]}
        else:
            logger.warning(f"Push notification failed for {device_token[:20]}...")
            return {"status": "failed", "token": device_token[:20]}

    except Exception as e:
        logger.error(f"Push notification error: {e}")
        raise


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
    name="tasks.notification_tasks.send_multicast_notification"
)
def send_multicast_notification(
    self,
    device_tokens: List[str],
    title: str,
    body: str,
    data: Optional[Dict] = None
) -> Dict:
    """
    Envia notificacao push para multiplos dispositivos.
    """
    if not device_tokens:
        return {"status": "skipped", "reason": "no tokens"}

    logger.info(f"Sending multicast notification to {len(device_tokens)} devices")

    try:
        firebase = get_firebase_service()
        success = firebase.send_multicast_notification(
            tokens=device_tokens,
            title=title,
            body=body,
            data=data or {}
        )

        return {
            "status": "sent" if success else "partial_failure",
            "device_count": len(device_tokens)
        }

    except Exception as e:
        logger.error(f"Multicast notification error: {e}")
        raise


# ==========================================
# PAYMENT NOTIFICATIONS
# ==========================================

@shared_task(
    bind=True,
    max_retries=3,
    name="tasks.notification_tasks.send_payment_confirmation_notification"
)
def send_payment_confirmation_notification(
    self,
    user_id: int,
    payment_method: str,
    amount: float
) -> Dict:
    """
    Envia notificacao de confirmacao de pagamento.
    """
    logger.info(f"Sending payment confirmation to user {user_id}")

    try:
        with get_sync_db() as db:
            # Buscar usuario
            stmt = select(User).where(User.id == user_id)
            result = db.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                return {"status": "skipped", "reason": "user not found"}

            # Formatar mensagem
            method_names = {
                "stripe": "Cartao de Credito",
                "pix": "Pix",
                "bitcoin": "Bitcoin Lightning",
                "wise": "Transferencia Wise",
                "nomad": "Transferencia Nomad"
            }
            method_name = method_names.get(payment_method, payment_method)

            title = "Pagamento Confirmado!"
            body = f"Seu pagamento de R$ {amount:.2f} via {method_name} foi confirmado. Obrigado!"

            # Enviar push se tiver token
            if user.device_token:
                send_push_notification.delay(
                    device_token=user.device_token,
                    title=title,
                    body=body,
                    data={
                        "type": "payment_confirmed",
                        "amount": str(amount),
                        "method": payment_method
                    }
                )

            # TODO: Enviar email tambem
            # send_email_notification.delay(user.email, title, body)

            return {"status": "queued", "user_id": user_id}

    except Exception as e:
        logger.error(f"Payment confirmation notification error: {e}")
        raise


@shared_task(
    bind=True,
    max_retries=3,
    name="tasks.notification_tasks.send_subscription_expiring_notification"
)
def send_subscription_expiring_notification(
    self,
    user_id: int,
    days_remaining: int
) -> Dict:
    """
    Notifica usuario sobre assinatura prestes a expirar.
    """
    logger.info(f"Sending expiring notification to user {user_id} ({days_remaining} days)")

    try:
        with get_sync_db() as db:
            stmt = select(User).where(User.id == user_id)
            result = db.execute(stmt)
            user = result.scalar_one_or_none()

            if not user or not user.device_token:
                return {"status": "skipped", "reason": "no user or token"}

            if days_remaining <= 1:
                title = "Sua assinatura expira amanha!"
                body = "Renove agora para continuar aproveitando todos os recursos do EVA."
            elif days_remaining <= 3:
                title = f"Sua assinatura expira em {days_remaining} dias"
                body = "Nao perca acesso aos seus cuidados. Renove sua assinatura."
            else:
                title = f"Lembrete: Assinatura expira em {days_remaining} dias"
                body = "Renovacao antecipada disponivel com desconto especial."

            send_push_notification.delay(
                device_token=user.device_token,
                title=title,
                body=body,
                data={
                    "type": "subscription_expiring",
                    "days_remaining": str(days_remaining)
                }
            )

            return {"status": "queued", "user_id": user_id, "days": days_remaining}

    except Exception as e:
        logger.error(f"Subscription expiring notification error: {e}")
        raise


# ==========================================
# ALERT NOTIFICATIONS
# ==========================================

@shared_task(
    bind=True,
    max_retries=5,
    name="tasks.notification_tasks.send_emergency_alert"
)
def send_emergency_alert(
    self,
    idoso_id: int,
    alert_type: str,
    message: str
) -> Dict:
    """
    Envia alerta de emergencia para todos os cuidadores de um idoso.
    """
    logger.warning(f"Sending emergency alert for idoso {idoso_id}: {alert_type}")

    try:
        with get_sync_db() as db:
            # Buscar todos os cuidadores do idoso
            stmt = select(Cuidador).where(Cuidador.idoso_id == idoso_id)
            result = db.execute(stmt)
            cuidadores = result.scalars().all()

            if not cuidadores:
                logger.warning(f"No cuidadores found for idoso {idoso_id}")
                return {"status": "no_cuidadores", "idoso_id": idoso_id}

            tokens = [c.device_token for c in cuidadores if c.device_token]

            if tokens:
                send_multicast_notification.delay(
                    device_tokens=tokens,
                    title=f"ALERTA: {alert_type}",
                    body=message,
                    data={
                        "type": "emergency_alert",
                        "alert_type": alert_type,
                        "idoso_id": str(idoso_id),
                        "priority": "high"
                    }
                )

            return {
                "status": "sent",
                "cuidadores_count": len(cuidadores),
                "tokens_count": len(tokens)
            }

    except Exception as e:
        logger.error(f"Emergency alert error: {e}")
        raise


@shared_task(
    bind=True,
    max_retries=3,
    name="tasks.notification_tasks.send_medication_reminder"
)
def send_medication_reminder(
    self,
    idoso_id: int,
    medication_name: str,
    dosage: str
) -> Dict:
    """
    Envia lembrete de medicamento.
    """
    logger.info(f"Sending medication reminder for idoso {idoso_id}: {medication_name}")

    try:
        with get_sync_db() as db:
            # Buscar cuidadores
            stmt = select(Cuidador).where(Cuidador.idoso_id == idoso_id)
            result = db.execute(stmt)
            cuidadores = result.scalars().all()

            tokens = [c.device_token for c in cuidadores if c.device_token]

            if tokens:
                send_multicast_notification.delay(
                    device_tokens=tokens,
                    title="Hora do Medicamento",
                    body=f"{medication_name} - {dosage}",
                    data={
                        "type": "medication_reminder",
                        "medication": medication_name,
                        "dosage": dosage,
                        "idoso_id": str(idoso_id)
                    }
                )

            return {"status": "sent", "tokens_count": len(tokens)}

    except Exception as e:
        logger.error(f"Medication reminder error: {e}")
        raise
