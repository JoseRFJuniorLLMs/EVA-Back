import pytest

@pytest.mark.asyncio
async def test_list_idosos_route(client):
    response = await client.get("/idosos/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 10  # Default limit rule

@pytest.mark.asyncio
async def test_create_idoso_route(client):
    idoso_data = {
        "nome": "Route Test Idoso",
        "telefone": "55555555",
        "data_nascimento": "1960-12-12"
    }
    response = await client.post("/idosos/", json=idoso_data)
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "Route Test Idoso"
    assert "id" in data

@pytest.mark.asyncio
async def test_list_agendamentos_route(client):
    response = await client.get("/agendamentos/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 10  # Default limit rule

@pytest.mark.asyncio
async def test_list_configs_route(client):
    response = await client.get("/config/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 10
