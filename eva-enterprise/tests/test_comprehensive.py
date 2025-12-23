import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_idosos_endpoints(client: AsyncClient):
    # GET /idosos/
    response = await client.get("/idosos/")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_agendamentos_endpoints(client: AsyncClient):
    # GET /agendamentos/
    response = await client.get("/agendamentos/")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_alertas_endpoints(client: AsyncClient):
    # GET /alertas/
    response = await client.get("/alertas/")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_medicamentos_endpoints(client: AsyncClient):
    # GET /medicamentos/sinais-vitais/relatorio/1
    response = await client.get("/medicamentos/sinais-vitais/relatorio/1")
    assert response.status_code in [200, 404]

@pytest.mark.asyncio
async def test_pagamentos_endpoints(client: AsyncClient):
    # GET /pagamentos/assinaturas
    response = await client.get("/pagamentos/assinaturas")
    assert response.status_code == 200
    # GET /pagamentos/audit
    response = await client.get("/pagamentos/audit")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_config_endpoints(client: AsyncClient):
    # GET /config/
    response = await client.get("/config/")
    assert response.status_code == 200
    # GET /config/prompts/
    response = await client.get("/config/prompts/")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_extras_endpoints(client: AsyncClient):
    # GET /extras/relatorios/idoso/1
    response = await client.get("/extras/relatorios/idoso/1")
    assert response.status_code in [200, 404]

@pytest.mark.asyncio
async def test_orquestrador_endpoints(client: AsyncClient):
    # GET /orquestrador/1
    response = await client.get("/orquestrador/1")
    assert response.status_code in [200, 404]

@pytest.mark.asyncio
async def test_protocolos_endpoints(client: AsyncClient):
    # GET /protocolos/1
    response = await client.get("/protocolos/1")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_historico_endpoints(client: AsyncClient):
    # GET /historico/
    response = await client.get("/historico/")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    # GET /health
    response = await client.get("/health")
    assert response.status_code == 200
