from fastapi import APIRouter, Depends, HTTPException
from typing import List
from schemas import FlowResponse, FlowCreate, FlowStepResponse
from datetime import datetime

router = APIRouter()

# --- Mock Database for Flows ---
# In a real scenario, this would be in a database table called 'workflows'
MOCK_FLOWS = [
    {
        "id": 1,
        "idoso_id": 1,
        "nome": "Protocolo de Queda",
        "etapas": [
            {"id": 101, "flow_id": 1, "delay": 0, "acao": "NOTIFY_WA", "vezes": 1, "contato": "Filha (Maria)", "status": "Ativo"},
            {"id": 102, "flow_id": 1, "delay": 2, "acao": "RETRY", "vezes": 3, "contato": None, "status": "Ativo"},
            {"id": 103, "flow_id": 1, "delay": 5, "acao": "NOTIFY_SMS", "vezes": 1, "contato": "Emergência", "status": "Pendente"}
        ]
    }
]

@router.get("/{idoso_id}", response_model=FlowResponse)
def get_flow(idoso_id: int):
    # Find active flow for idoso
    flow = next((f for f in MOCK_FLOWS if f["idoso_id"] == idoso_id), None)
    if not flow:
        # Return a default empty/template flow if none exists, or 404
        # Frontend expects a flow object
        return {
            "id": 0,
            "idoso_id": idoso_id,
            "nome": "Nenhum protocolo ativo",
            "etapas": []
        }
    return flow

@router.post("/", response_model=FlowResponse)
def create_flow(flow_data: FlowCreate):
    new_id = len(MOCK_FLOWS) + 1
    new_flow = {
        "id": new_id,
        "idoso_id": flow_data.idoso_id,
        "nome": flow_data.nome,
        "etapas": []
    }
    
    # Process steps
    for idx, step in enumerate(flow_data.etapas):
        new_step = step.model_dump()
        new_step["id"] = int(f"{new_id}{idx}")
        new_step["flow_id"] = new_id
        new_flow["etapas"].append(new_step)
        
    MOCK_FLOWS.append(new_flow)
    return new_flow
