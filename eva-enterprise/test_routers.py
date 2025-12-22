"""
Script para verificar se todos os routers estão sendo registrados corretamente
"""
import sys
sys.path.insert(0, 'd:\\dev\\EVA-back\\eva-enterprise')

from fastapi import FastAPI

# Imports from api package
from api.routes_alertas import router as alertas_router
from api.routes_config import router as config_router
from api.routes_extras import router as extras_router
from api.routes_idosos import router as idosos_router
from api.routes_medicamentos import router as medicamentos_router
from api.routes_pagamentos import router as pagamentos_router
from api.calls import router as calls_router
from api.routes_agendamentos import router as agendamentos_router
from api.routes_orquestrador import router as orquestrador_router

app = FastAPI(
    title="EVA Enterprise API - TEST",
    description="API set for Eva Enterprise",
    version="6.0"
)

# Inclui todos os routers
app.include_router(alertas_router, prefix="/alertas", tags=["Alertas e Insights"])
app.include_router(config_router, prefix="/configs", tags=["Configurações"])
app.include_router(extras_router, prefix="/extras", tags=["Extras e Relatórios"])
app.include_router(orquestrador_router, prefix="/orquestrador", tags=["Orquestrador de Fluxos"])
app.include_router(idosos_router, prefix="/idosos", tags=["Idosos e Familiares"])
app.include_router(medicamentos_router, prefix="/medicamentos", tags=["Medicamentos e Sinais Vitais"])
app.include_router(pagamentos_router, prefix="/pagamentos", tags=["Pagamentos e Auditoria"])
app.include_router(calls_router, tags=["Chamadas"])
app.include_router(agendamentos_router, prefix="/agendamentos", tags=["Agendamentos e Histórico"])

print("\n" + "="*60)
print("✅ VERIFICAÇÃO DE ROUTERS")
print("="*60)

# Lista todas as rotas registradas
routes_by_tag = {}
for route in app.routes:
    if hasattr(route, 'tags') and route.tags:
        for tag in route.tags:
            if tag not in routes_by_tag:
                routes_by_tag[tag] = []
            routes_by_tag[tag].append(f"{route.methods} {route.path}")

print(f"\n📊 Total de rotas: {len(app.routes)}")
print(f"📊 Total de tags: {len(routes_by_tag)}\n")

for tag, routes in sorted(routes_by_tag.items()):
    print(f"\n🏷️  {tag} ({len(routes)} rotas):")
    for route in sorted(routes):
        print(f"   {route}")

print("\n" + "="*60)
print("Se você vê múltiplas tags acima, os routers estão OK!")
print("="*60 + "\n")
