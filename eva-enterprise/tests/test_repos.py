import pytest
from database.repositories.idoso_repo import IdosoRepository
from database.repositories.agendamento_repo import AgendamentoRepository
from datetime import datetime

@pytest.mark.asyncio
async def test_create_and_get_idoso(db_session):
    repo = IdosoRepository(db_session)
    idoso_data = {
        "nome": "Test Idoso",
        "telefone": "123456789",
        "cpf": "123.456.789-00",
        "data_nascimento": "1950-01-01"
    }
    
    # Test Create
    new_idoso = await repo.create(idoso_data)
    assert new_idoso.id is not None
    assert new_idoso.nome == "Test Idoso"
    
    # Test Get by ID
    fetched = await repo.get_by_id(new_idoso.id)
    assert fetched.nome == "Test Idoso"

@pytest.mark.asyncio
async def test_create_agendamento(db_session):
    # Setup Idoso first
    idoso_repo = IdosoRepository(db_session)
    idoso = await idoso_repo.create({
        "nome": "Idoso for Agenda",
        "telefone": "987654321",
        "data_nascimento": "1940-05-05"
    })
    
    repo = AgendamentoRepository(db_session)
    agendamento_data = {
        "idoso_id": idoso.id,
        "tipo": "medicamento",
        "data_hora_agendada": datetime.now(),
        "status": "agendado"
    }
    
    new_agenda = await repo.create(agendamento_data)
    assert new_agenda.id is not None
    assert new_agenda.idoso_id == idoso.id
