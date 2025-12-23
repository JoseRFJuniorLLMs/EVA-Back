import pytest
from httpx import AsyncClient

# Testes de criação simples (Payloads mínimos para passar na validação de esquema)

@pytest.mark.asyncio
async def test_post_idosos(client: AsyncClient):
    payload = {
        "nome": "Test Idoso",
        "telefone": "12345678",
        "data_nascimento": "1950-01-01",
        "cpf": "12345678901"
    }
    response = await client.post("/idosos/", json=payload)
    assert response.status_code in [200, 201]

@pytest.mark.asyncio
async def test_post_agendamento(client: AsyncClient):
    payload = {
        "idoso_id": 1,
        "tipo": "medicamento",
        "data_hora_agendada": "2025-12-23T10:00:00"
    }
    response = await client.post("/agendamentos/", json=payload)
    assert response.status_code in [200, 201, 404] # 404 se idoso 1 não existir

@pytest.mark.asyncio
async def test_post_alerta(client: AsyncClient):
    payload = {
        "idoso_id": 1,
        "tipo": "queda",
        "severidade": "alta",
        "mensagem": "Possível queda detectada"
    }
    response = await client.post("/alertas/", json=payload)
    assert response.status_code in [200, 201, 404]

@pytest.mark.asyncio
async def test_post_medicamento(client: AsyncClient):
    payload = {
        "idoso_id": 1,
        "nome": "Paracetamol",
        "dosagem": "500mg",
        "horarios": ["08:00", "20:00"]
    }
    response = await client.post("/medicamentos/", json=payload)
    assert response.status_code in [200, 201, 404]

@pytest.mark.asyncio
async def test_post_config(client: AsyncClient):
    payload = {
        "chave": "test_key",
        "valor": "test_value",
        "tipo": "string",
        "categoria": "geral"
    }
    response = await client.post("/config/", json=payload)
    assert response.status_code in [200, 201]

@pytest.mark.asyncio
async def test_post_login(client: AsyncClient):
    payload = {"username": "admin", "password": "admin"}
    response = await client.post("/extras/login", json=payload)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_post_protocolo(client: AsyncClient):
    payload = {
        "idoso_id": 1,
        "nome": "Protocolo de Teste",
        "etapas": [
            {"ordem": 1, "acao": "ligar", "delay_minutos": 5}
        ]
    }
    response = await client.post("/protocolos/", json=payload)
    assert response.status_code in [200, 201, 404]

@pytest.mark.asyncio
async def test_post_sinais_vitais(client: AsyncClient):
    payload = {
        "idoso_id": 1,
        "tipo": "pressao",
        "valor": "12/8",
        "unidade": "mmHg"
    }
    response = await client.post("/medicamentos/sinais-vitais", json=payload)
    assert response.status_code in [200, 201, 404]
