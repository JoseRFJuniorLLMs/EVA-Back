"""
Script de diagnóstico para verificar por que os routers não aparecem
"""
import sys
import traceback

sys.path.insert(0, 'd:\\dev\\EVA-back\\eva-enterprise')

print("="*60)
print("DIAGNÓSTICO DE ROUTERS")
print("="*60)

# Testa cada import individualmente
routers_to_test = [
    ("alertas", "api.routes_alertas"),
    ("config", "api.routes_config"),
    ("extras", "api.routes_extras"),
    ("idosos", "api.routes_idosos"),
    ("medicamentos", "api.routes_medicamentos"),
    ("pagamentos", "api.routes_pagamentos"),
    ("calls", "api.calls"),
    ("agendamentos", "api.routes_agendamentos"),
    ("orquestrador", "api.routes_orquestrador"),
]

print("\n1. Testando imports individuais:")
print("-"*60)
failed_imports = []
for name, module in routers_to_test:
    try:
        exec(f"from {module} import router")
        print(f"✅ {name:15} - OK")
    except Exception as e:
        print(f"❌ {name:15} - ERRO: {str(e)[:50]}")
        failed_imports.append((name, module, e))

if failed_imports:
    print("\n⚠️ ERROS DETALHADOS:")
    print("-"*60)
    for name, module, error in failed_imports:
        print(f"\n{name} ({module}):")
        traceback.print_exception(type(error), error, error.__traceback__)

print("\n2. Testando importação do main.py:")
print("-"*60)
try:
    from main import app
    print(f"✅ main.py importado com sucesso")
    print(f"✅ Total de rotas registradas: {len(app.routes)}")
    
    # Conta rotas por tag
    tags_count = {}
    for route in app.routes:
        if hasattr(route, 'tags') and route.tags:
            for tag in route.tags:
                tags_count[tag] = tags_count.get(tag, 0) + 1
    
    print(f"\n3. Rotas por tag:")
    print("-"*60)
    for tag, count in sorted(tags_count.items()):
        print(f"  {tag:40} - {count} rotas")
    
    if len(tags_count) < 5:
        print(f"\n❌ PROBLEMA: Esperado 9 tags, encontrado {len(tags_count)}")
        print("   Alguns routers não foram registrados!")
    else:
        print(f"\n✅ SUCESSO: {len(tags_count)} tags encontradas")
        
except Exception as e:
    print(f"❌ Erro ao importar main.py: {e}")
    traceback.print_exc()

print("\n" + "="*60)
