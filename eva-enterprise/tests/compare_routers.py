"""
Compara as definições dos routers para encontrar diferenças
"""
import sys
sys.path.insert(0, '..')

print("="*70)
print("COMPARAÇÃO: calls.py vs routes_alertas.py")
print("="*70)

# Importa os dois routers
from api.calls import router as calls_router
from api.routes_alertas import router as alertas_router

print(f"\n📊 calls_router:")
print(f"   - Número de rotas: {len(calls_router.routes)}")
print(f"   - Prefix: {calls_router.prefix}")
print(f"   - Tags: {calls_router.tags}")
print(f"   - Tipo: {type(calls_router)}")

print(f"\n📊 alertas_router:")
print(f"   - Número de rotas: {len(alertas_router.routes)}")
print(f"   - Prefix: {alertas_router.prefix}")
print(f"   - Tags: {alertas_router.tags}")
print(f"   - Tipo: {type(alertas_router)}")

print(f"\n📋 Rotas do calls_router:")
for route in calls_router.routes:
    print(f"   {list(route.methods)} {route.path}")

print(f"\n📋 Rotas do alertas_router:")
for route in alertas_router.routes:
    print(f"   {list(route.methods)} {route.path}")

print("\n" + "="*70)
