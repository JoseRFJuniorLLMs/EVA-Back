import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_historico_route(client: AsyncClient):
    response = await client.get("/historico/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_protocolos_route(client: AsyncClient):
    # Test for idoso_id=1
    response = await client.get("/protocolos/1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_consumo_route(client: AsyncClient):
    # Test for idoso_id=1
    response = await client.get("/pagamentos/consumo/1")
    # Might be 404 if no data, but the route should exist
    assert response.status_code in [200, 404]

@pytest.mark.asyncio
async def test_audit_limit(client: AsyncClient):
    response = await client.get("/pagamentos/audit")
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 10
