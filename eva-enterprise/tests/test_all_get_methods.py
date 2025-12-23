import pytest
from httpx import AsyncClient

# Lista de todos os endpoints GET mapeados
GET_ENDPOINTS = [
    ("/protocolos/1", [200, 404]),
    ("/pagamentos/assinaturas", [200]),
    ("/pagamentos/assinaturas/1", [200, 404]),
    ("/pagamentos/consumo/1", [200, 404]),
    ("/pagamentos/audit", [200]),
    ("/orquestrador/1", [200, 404]),
    ("/medicamentos/1", [200, 404]),
    ("/medicamentos/sinais-vitais/1", [200, 404]),
    ("/medicamentos/sinais-vitais/relatorio/1", [200, 404]),
    ("/idosos/", [200]),
    ("/idosos/1", [200, 404]),
    ("/idosos/1/familiares", [200, 404]),
    ("/idosos/1/legado-digital", [200, 404]),
    ("/idosos/1/perfil-clinico", [200, 404]),
    ("/idosos/1/memorias", [200, 404]),
    ("/historico/", [200]),
    ("/historico/1", [200, 404]),
    ("/extras/relatorios/idoso/1", [200, 404]),
    ("/config/prompts/", [200]),
    ("/config/functions/", [200]),
    ("/config/circuit-breakers/", [200]),
    ("/config/rate-limits/", [200]),
    ("/config/", [200]),
    ("/config/some_key", [200, 404]),
    ("/alertas/", [200]),
    ("/alertas/1", [200, 404]),
    ("/alertas/psicologia-insights/1", [200, 404]),
    ("/alertas/topicos-afetivos/1", [200, 404]),
    ("/alertas/psicologia-insights/historico/1/", [200, 404]),
    ("/agendamentos/", [200]),
    ("/agendamentos/1", [200, 404]),
    # Placeholders
    ("/metricas/", [200]),
    ("/contatos-alerta/", [200]),
    ("/timeline/", [200]),
    ("/formas-pagamento/", [200]),
    ("/biografias/", [200]),
    ("/finops/", [200]),
    ("/fluxos-alerta/", [200]),
    ("/genealogia/", [200]),
    ("/legacy-assets/", [200]),
    ("/emotional-analytics/", [200]),
]

@pytest.mark.asyncio
@pytest.mark.parametrize("path, expected_status", GET_ENDPOINTS)
async def test_all_get_endpoints_status(client: AsyncClient, path, expected_status):
    """Testa se cada endpoint GET responde com um status esperado (200 ou 404)."""
    response = await client.get(path)
    assert response.status_code in expected_status, f"Erro em {path}: {response.status_code} não está em {expected_status}"
