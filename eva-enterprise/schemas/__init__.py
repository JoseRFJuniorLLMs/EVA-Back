"""
Schemas __init__.py
Exporta todos os schemas para facilitar imports
"""
from .checkout import (
    StripeCheckoutRequest,
    StripeCheckoutResponse,
    AsaasPixRequest,
    AsaasPixResponse,
    BitcoinInvoiceRequest,
    BitcoinInvoiceResponse,
    InternationalInstructionsRequest,
    InternationalInstructionsResponse,
    ReceiptUploadResponse,
    PaymentMethodInfo
)

from .subscription import (
    SubscriptionCreate,
    SubscriptionResponse,
    SubscriptionUpdate,
    SubscriptionCancelRequest,
    SubscriptionHistoryItem
)

from .transaction import (
    TransactionCreate,
    TransactionResponse,
    TransactionStatusUpdate,
    TransactionListResponse,
    TransactionStatsResponse
)

from .webhook import (
    StripeWebhookEvent,
    AsaasWebhookEvent,
    OpenNodeWebhookEvent,
    WebhookProcessedResponse
)

__all__ = [
    # Checkout
    "StripeCheckoutRequest",
    "StripeCheckoutResponse",
    "AsaasPixRequest",
    "AsaasPixResponse",
    "BitcoinInvoiceRequest",
    "BitcoinInvoiceResponse",
    "InternationalInstructionsRequest",
    "InternationalInstructionsResponse",
    "ReceiptUploadResponse",
    "PaymentMethodInfo",
    
    # Subscription
    "SubscriptionCreate",
    "SubscriptionResponse",
    "SubscriptionUpdate",
    "SubscriptionCancelRequest",
    "SubscriptionHistoryItem",
    
    # Transaction
    "TransactionCreate",
    "TransactionResponse",
    "TransactionStatusUpdate",
    "TransactionListResponse",
    "TransactionStatsResponse",
    
    # Webhook
    "StripeWebhookEvent",
    "AsaasWebhookEvent",
    "OpenNodeWebhookEvent",
    "WebhookProcessedResponse",
]

# Import everything from the main legacy schema file
from .main import *
