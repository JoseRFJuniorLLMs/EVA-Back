"""
API Routes Package
Exporta todos os routers para facilitar imports no main.py
"""
# Rotas existentes (mantidas para compatibilidade)
from . import (
    routes_idosos,
    routes_agendamentos,
    routes_alertas,
    routes_medicamentos,
    routes_pagamentos,
    routes_config,
    routes_extras,
    routes_orquestrador,
    routes_placeholders,
    routes_protocolos,
    routes_historico,
    routes_assinaturas,
    routes_ia,
    routes_cuidadores,
    routes_auth,
    routes_usuarios_saude,
    routes_saude,
    routes_dashboard_saude,
    routes_dashboard,
    routes_voice
)

# Financial Hub Routes (NOVO)
from . import (
    routes_checkout,
    routes_webhooks,
    routes_subscriptions,
    routes_admin_payments
)

__all__ = [
    # Rotas existentes
    "routes_idosos",
    "routes_agendamentos",
    "routes_alertas",
    "routes_medicamentos",
    "routes_pagamentos",
    "routes_config",
    "routes_extras",
    "routes_orquestrador",
    "routes_placeholders",
    "routes_protocolos",
    "routes_historico",
    "routes_assinaturas",
    "routes_ia",
    "routes_cuidadores",
    "routes_auth",
    "routes_usuarios_saude",
    "routes_saude",
    "routes_dashboard_saude",
    "routes_dashboard",
    "routes_voice",
    # Financial Hub
    "routes_checkout",
    "routes_webhooks",
    "routes_subscriptions",
    "routes_admin_payments",
]
