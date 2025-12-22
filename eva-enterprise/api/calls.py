"""
Calls API - Endpoints para disparar chamadas (REFATORADO)
Agora suporta agendamento_id e passa para o TwiML
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from services.call_orchestrator import CallOrchestrator
from config.settings import settings
from database.connection import SessionLocal
from database.repositories.agendamento_repo import AgendamentoRepository

router = APIRouter()
orchestrator = CallOrchestrator()

from fastapi import Body, HTTPException


@router.post("/make-call")
async def make_call(agendamento_id: int = Body(..., embed=True)):
    """
    Dispara ligação para um agendamento específico

    Args:
        agendamento_id: ID do agendamento a ser executado (enviado no body JSON)

    Returns:
        Dict com SID da chamada e status
    """
    db = SessionLocal()
    try:
        # 1. Busca agendamento
        repo = AgendamentoRepository(db)
        agendamento = repo.get_by_id(agendamento_id)

        if not agendamento:
            raise HTTPException(status_code=404, detail="Agendamento não encontrado")

        if agendamento.status not in ['pendente', 'retry_agendado']:
            raise HTTPException(
                status_code=400,
                detail=f"Agendamento em status inválido: {agendamento.status}"
            )

        # 2. Atualiza status para "em_andamento"
        repo.update_status(agendamento_id, 'em_andamento')

        # 3. Dispara ligação via Twilio
        sid = await orchestrator.initiate_call(
            to_number=agendamento.telefone,
            agendamento_id=agendamento_id
        )

        print(f"📞 Ligação disparada: SID={sid}, Agendamento={agendamento_id}")

        return {
            "sid": sid,
            "agendamento_id": agendamento_id,
            "status": "Eva está ligando!",
            "idoso_nome": agendamento.nome_idoso
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro ao disparar ligação: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.post("/twiml")
async def twiml_endpoint(agendamento_id: int):
    """
    Retorna TwiML para conectar ao WebSocket
    Twilio chama este endpoint quando a ligação é atendida
    
    Args:
        agendamento_id: ID do agendamento (passado via query string)
    
    Returns:
        XML Response com instrução de Stream
    """
    print(f"📋 TwiML solicitado para agendamento #{agendamento_id}")
    
    # Valida que agendamento existe
    db = SessionLocal()
    try:
        repo = AgendamentoRepository(db)
        agendamento = repo.get_by_id(agendamento_id)
        
        if not agendamento:
            # Se não existe, retorna TwiML de erro
            xml_response = """<?xml version="1.0" encoding="UTF-8"?>
            <Response>
                <Say voice="Polly.Camila" language="pt-BR">
                    Desculpe, ocorreu um erro. Por favor, tente novamente mais tarde.
                </Say>
                <Hangup/>
            </Response>"""
            return Response(content=xml_response, media_type="text/xml")
    finally:
        db.close()
    
    # Monta URL do WebSocket COM agendamento_id no path
    ws_url = f"wss://{settings.SERVICE_DOMAIN}/media-stream/{agendamento_id}"
    
    xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Connect>
            <Stream url="{ws_url}" />
        </Connect>
    </Response>"""
    
    return Response(content=xml_response, media_type="text/xml")


@router.get("/status/{agendamento_id}")
async def get_call_status(agendamento_id: int):
    """
    Consulta status de um agendamento
    
    Args:
        agendamento_id: ID do agendamento
    
    Returns:
        Dict com status e dados do agendamento
    """
    db = SessionLocal()
    try:
        repo = AgendamentoRepository(db)
        agendamento = repo.get_details_with_idoso(agendamento_id)
        
        if not agendamento:
            raise HTTPException(status_code=404, detail="Agendamento não encontrado")
        
        return {
            "id": agendamento.id,
            "idoso_nome": agendamento.nome_idoso,
            "status": agendamento.status,
            "tentativas_realizadas": agendamento.tentativas_realizadas,
            "horario_agendado": agendamento.horario.isoformat() if agendamento.horario else None
        }
    finally:
        db.close()


@router.post("/cancel/{agendamento_id}")
async def cancel_call(agendamento_id: int):
    """
    Cancela um agendamento
    
    Args:
        agendamento_id: ID do agendamento
    
    Returns:
        Dict confirmando cancelamento
    """
    db = SessionLocal()
    try:
        repo = AgendamentoRepository(db)
        agendamento = repo.update_status(agendamento_id, 'cancelado')
        
        if not agendamento:
            raise HTTPException(status_code=404, detail="Agendamento não encontrado")
        
        return {
            "message": "Agendamento cancelado com sucesso",
            "agendamento_id": agendamento_id
        }
    finally:
        db.close()