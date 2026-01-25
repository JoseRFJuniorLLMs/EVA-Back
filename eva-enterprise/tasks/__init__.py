"""
EVA Enterprise Tasks
====================
Modulo de tasks Celery para processamento assincrono.

Uso:
    from tasks import process_stripe_webhook, send_push_notification

    # Disparar task
    process_stripe_webhook.delay(event_data)

    # Disparar com options
    send_push_notification.apply_async(
        args=[token, title, body],
        countdown=5  # delay de 5 segundos
    )
"""

from tasks.webhook_tasks import (
    process_stripe_webhook,
    process_asaas_webhook,
    process_opennode_webhook,
    process_wise_webhook,
)

from tasks.notification_tasks import (
    send_push_notification,
    send_multicast_notification,
    send_payment_confirmation_notification,
    send_subscription_expiring_notification,
)

from tasks.reconciliation_tasks import (
    reconcile_wise_transactions,
    reconcile_all_pending_transactions,
)

from tasks.scheduled_tasks import (
    cleanup_pending_transactions,
    check_expiring_subscriptions,
    payment_health_check,
)

__all__ = [
    # Webhook Tasks
    "process_stripe_webhook",
    "process_asaas_webhook",
    "process_opennode_webhook",
    "process_wise_webhook",
    # Notification Tasks
    "send_push_notification",
    "send_multicast_notification",
    "send_payment_confirmation_notification",
    "send_subscription_expiring_notification",
    # Reconciliation Tasks
    "reconcile_wise_transactions",
    "reconcile_all_pending_transactions",
    # Scheduled Tasks
    "cleanup_pending_transactions",
    "check_expiring_subscriptions",
    "payment_health_check",
]
