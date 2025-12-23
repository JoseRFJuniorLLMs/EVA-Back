import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_put_idoso(client: AsyncClient):
    # Tenta atualizar um idoso inexistente (404 esperado) ou valida a rota
    payload = {"nome": "Updated Name"}
    response = await client.put("/idosos/999", json=payload)
    assert response.status_code in [200, 404]

@pytest.mark.asyncio
async def test_put_config_prompt(client: AsyncClient):
    payload = {"nome": "Updated Prompt", "conteudo": "New content"}
    response = await client.put("/config/prompts/999", json=payload)
    assert response.status_code in [200, 404]

@pytest.mark.asyncio
async def test_put_config_rate_limit(client: AsyncClient):
    # Rota: /config/rate-limits/{id}?limit=100&interval=60
    response = await client.put("/config/rate-limits/999?limit=100&interval=60")
    assert response.status_code in [200, 404]

@pytest.mark.asyncio
async def test_put_config_general(client: AsyncClient):
    payload = {"valor": "new_value"}
    response = await client.put("/config/999", json=payload)
    assert response.status_code in [200, 404]

@pytest.mark.asyncio
async def test_put_agendamento(client: AsyncClient):
    payload = {"status": "CONCLUIDO"}
    response = await client.put("/agendamentos/999", json=payload)
    assert response.status_code in [200, 404]
