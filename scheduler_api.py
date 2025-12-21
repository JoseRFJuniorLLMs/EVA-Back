import os, datetime, asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from twilio.rest import Client
from database import SessionLocal, Agendamento, Alerta, Idoso, Familiar
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# CORS configurado
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scheduler = AsyncIOScheduler()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
SERVICE_DOMAIN = os.getenv("SERVICE_DOMAIN")


# ====================================
# MODELOS DE DADOS PARA A API
# ====================================

class IdosoRequest(BaseModel):
    nome: str
    telefone: str
    endereco: Optional[str] = ""
    condicoes_medicas: Optional[str] = ""
    medicamentos_regulares: Optional[str] = ""


class FamiliarRequest(BaseModel):
    nome: str
    parentesco: Optional[str] = ""
    telefone: str
    email: Optional[str] = ""
    eh_responsavel: bool = False


class AgendamentoRequest(BaseModel):
    idoso_id: int
    hora_iso: str
    remedios: str


# ====================================
# ENDPOINTS PARA IDOSOS
# ====================================

@app.post("/idosos")
async def criar_idoso(request: IdosoRequest):
    """Cria um novo cadastro de idoso"""
    db = SessionLocal()
    try:
        novo_idoso = Idoso(
            nome=request.nome,
            telefone=request.telefone,
            endereco=request.endereco,
            condicoes_medicas=request.condicoes_medicas,
            medicamentos_regulares=request.medicamentos_regulares
        )

        db.add(novo_idoso)
        db.commit()
        db.refresh(novo_idoso)

        return {
            "message": "Idoso cadastrado com sucesso",
            "idoso": {
                "id": novo_idoso.id,
                "nome": novo_idoso.nome,
                "telefone": novo_idoso.telefone,
                "endereco": novo_idoso.endereco,
                "condicoes_medicas": novo_idoso.condicoes_medicas,
                "medicamentos_regulares": novo_idoso.medicamentos_regulares
            }
        }
    finally:
        db.close()


@app.get("/idosos")
async def listar_idosos():
    """Lista todos os idosos cadastrados"""
    db = SessionLocal()
    try:
        idosos = db.query(Idoso).order_by(Idoso.nome).all()

        return {
            "total": len(idosos),
            "idosos": [
                {
                    "id": i.id,
                    "nome": i.nome,
                    "telefone": i.telefone,
                    "endereco": i.endereco,
                    "condicoes_medicas": i.condicoes_medicas,
                    "medicamentos_regulares": i.medicamentos_regulares
                }
                for i in idosos
            ]
        }
    finally:
        db.close()


@app.get("/idosos/{idoso_id}")
async def obter_idoso(idoso_id: int):
    """Obtém os dados de um idoso específico"""
    db = SessionLocal()
    try:
        idoso = db.query(Idoso).filter(Idoso.id == idoso_id).first()

        if not idoso:
            raise HTTPException(status_code=404, detail="Idoso não encontrado")

        return {
            "id": idoso.id,
            "nome": idoso.nome,
            "telefone": idoso.telefone,
            "endereco": idoso.endereco,
            "condicoes_medicas": idoso.condicoes_medicas,
            "medicamentos_regulares": idoso.medicamentos_regulares
        }
    finally:
        db.close()


@app.put("/idosos/{idoso_id}")
async def atualizar_idoso(idoso_id: int, request: IdosoRequest):
    """Atualiza os dados de um idoso"""
    db = SessionLocal()
    try:
        idoso = db.query(Idoso).filter(Idoso.id == idoso_id).first()

        if not idoso:
            raise HTTPException(status_code=404, detail="Idoso não encontrado")

        idoso.nome = request.nome
        idoso.telefone = request.telefone
        idoso.endereco = request.endereco
        idoso.condicoes_medicas = request.condicoes_medicas
        idoso.medicamentos_regulares = request.medicamentos_regulares

        db.commit()
        db.refresh(idoso)

        return {
            "message": "Idoso atualizado com sucesso",
            "idoso": {
                "id": idoso.id,
                "nome": idoso.nome,
                "telefone": idoso.telefone,
                "endereco": idoso.endereco,
                "condicoes_medicas": idoso.condicoes_medicas,
                "medicamentos_regulares": idoso.medicamentos_regulares
            }
        }
    finally:
        db.close()


@app.delete("/idosos/{idoso_id}")
async def excluir_idoso(idoso_id: int):
    """Exclui um idoso"""
    db = SessionLocal()
    try:
        idoso = db.query(Idoso).filter(Idoso.id == idoso_id).first()

        if not idoso:
            raise HTTPException(status_code=404, detail="Idoso não encontrado")

        # Verifica se há agendamentos pendentes
        agendamentos_pendentes = db.query(Agendamento).filter(
            Agendamento.idoso_id == idoso_id,
            Agendamento.status == "pendente"
        ).count()

        if agendamentos_pendentes > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Não é possível excluir. Existem {agendamentos_pendentes} agendamento(s) pendente(s)"
            )

        db.delete(idoso)
        db.commit()

        return {"message": "Idoso excluído com sucesso"}
    finally:
        db.close()


# ====================================
# ENDPOINTS PARA FAMILIARES
# ====================================

@app.post("/familiares")
async def criar_familiar(request: FamiliarRequest):
    """Cria um novo cadastro de familiar"""
    db = SessionLocal()
    try:
        novo_familiar = Familiar(
            nome=request.nome,
            parentesco=request.parentesco,
            telefone=request.telefone,
            email=request.email,
            eh_responsavel=request.eh_responsavel
        )

        db.add(novo_familiar)
        db.commit()
        db.refresh(novo_familiar)

        return {
            "message": "Familiar cadastrado com sucesso",
            "familiar": {
                "id": novo_familiar.id,
                "nome": novo_familiar.nome,
                "parentesco": novo_familiar.parentesco,
                "telefone": novo_familiar.telefone,
                "email": novo_familiar.email,
                "eh_responsavel": novo_familiar.eh_responsavel
            }
        }
    finally:
        db.close()


@app.get("/familiares")
async def listar_familiares():
    """Lista todos os familiares cadastrados"""
    db = SessionLocal()
    try:
        familiares = db.query(Familiar).order_by(Familiar.nome).all()

        return {
            "total": len(familiares),
            "familiares": [
                {
                    "id": f.id,
                    "nome": f.nome,
                    "parentesco": f.parentesco,
                    "telefone": f.telefone,
                    "email": f.email,
                    "eh_responsavel": f.eh_responsavel
                }
                for f in familiares
            ]
        }
    finally:
        db.close()


@app.put("/familiares/{familiar_id}")
async def atualizar_familiar(familiar_id: int, request: FamiliarRequest):
    """Atualiza os dados de um familiar"""
    db = SessionLocal()
    try:
        familiar = db.query(Familiar).filter(Familiar.id == familiar_id).first()

        if not familiar:
            raise HTTPException(status_code=404, detail="Familiar não encontrado")

        familiar.nome = request.nome
        familiar.parentesco = request.parentesco
        familiar.telefone = request.telefone
        familiar.email = request.email
        familiar.eh_responsavel = request.eh_responsavel

        db.commit()
        db.refresh(familiar)

        return {
            "message": "Familiar atualizado com sucesso",
            "familiar": {
                "id": familiar.id,
                "nome": familiar.nome,
                "parentesco": familiar.parentesco,
                "telefone": familiar.telefone,
                "email": familiar.email,
                "eh_responsavel": familiar.eh_responsavel
            }
        }
    finally:
        db.close()


@app.delete("/familiares/{familiar_id}")
async def excluir_familiar(familiar_id: int):
    """Exclui um familiar"""
    db = SessionLocal()
    try:
        familiar = db.query(Familiar).filter(Familiar.id == familiar_id).first()

        if not familiar:
            raise HTTPException(status_code=404, detail="Familiar não encontrado")

        db.delete(familiar)
        db.commit()

        return {"message": "Familiar excluído com sucesso"}
    finally:
        db.close()


# ====================================
# SCHEDULER E LIGAÇÕES
# ====================================

async def verificar_e_disparar():
    """Verifica agendamentos pendentes e dispara ligações na hora certa"""
    db = SessionLocal()
    try:
        agora = datetime.datetime.now()

        # Busca agendamentos que precisam de ligação agora
        pendentes = db.query(Agendamento).filter(
            Agendamento.horario <= agora,
            Agendamento.status == "pendente"
        ).all()

        if not pendentes:
            return

        twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        for job in pendentes:
            try:
                print(f"⏰ Hora de ligar para {job.nome_idoso} (ID: {job.id})")
                print(f"   📞 Telefone: {job.telefone}")
                print(f"   💊 Remédios: {job.remedios}")

                # Faz a ligação via Twilio
                call = twilio_client.calls.create(
                    url=f"https://{SERVICE_DOMAIN}/twiml?agendamento_id={job.id}",
                    to=job.telefone,
                    from_=TWILIO_PHONE_NUMBER
                )

                # Atualiza o status para "ligado"
                job.status = "ligado"
                db.commit()

                print(f"   ✓ Ligação iniciada - SID: {call.sid}")

            except Exception as e:
                print(f"   ✗ Erro ao ligar para {job.nome_idoso}: {e}")

                # Registra erro no sistema de alertas
                novo_alerta = Alerta(
                    tipo="ERRO_SISTEMA",
                    descricao=f"Falha ao ligar para {job.nome_idoso} (ID: {job.id}): {str(e)}"
                )
                db.add(novo_alerta)
                db.commit()

    finally:
        db.close()


# ====================================
# ENDPOINTS PARA AGENDAMENTOS
# ====================================

@app.post("/agendar")
async def agendar(request: AgendamentoRequest):
    """Endpoint para a família agendar uma ligação da Eva"""
    db = SessionLocal()
    try:
        # Busca o idoso
        idoso = db.query(Idoso).filter(Idoso.id == request.idoso_id).first()

        if not idoso:
            raise HTTPException(status_code=404, detail="Idoso não encontrado")

        # Valida o formato da data
        try:
            horario = datetime.datetime.fromisoformat(request.hora_iso)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Formato de data inválido. Use ISO 8601, exemplo: 2025-12-20T14:30:00"
            )

        # Verifica se já existe agendamento para este horário e idoso
        existe = db.query(Agendamento).filter(
            Agendamento.idoso_id == request.idoso_id,
            Agendamento.horario == horario,
            Agendamento.status == "pendente"
        ).first()

        if existe:
            raise HTTPException(
                status_code=409,
                detail=f"Já existe um agendamento para {idoso.nome} neste horário"
            )

        # Cria novo agendamento
        novo = Agendamento(
            idoso_id=idoso.id,
            nome_idoso=idoso.nome,
            telefone=idoso.telefone,
            horario=horario,
            remedios=request.remedios,
            status="pendente"
        )

        db.add(novo)
        db.commit()
        db.refresh(novo)

        print(f"✓ Novo agendamento criado:")
        print(f"   ID: {novo.id}")
        print(f"   Paciente: {idoso.nome}")
        print(f"   Horário: {horario.strftime('%d/%m/%Y %H:%M')}")
        print(f"   Remédios: {request.remedios}")

        return {
            "message": "Agendamento criado com sucesso",
            "agendamento_id": novo.id,
            "nome": idoso.nome,
            "horario": horario.isoformat(),
            "status": "pendente"
        }

    finally:
        db.close()


@app.get("/agendamentos")
async def listar_agendamentos(status: str = None):
    """Lista todos os agendamentos"""
    db = SessionLocal()
    try:
        query = db.query(Agendamento)

        if status:
            query = query.filter(Agendamento.status == status)

        agendamentos = query.order_by(Agendamento.horario.desc()).all()

        return {
            "total": len(agendamentos),
            "agendamentos": [
                {
                    "id": a.id,
                    "nome": a.nome_idoso,
                    "telefone": a.telefone,
                    "horario": a.horario.isoformat(),
                    "remedios": a.remedios,
                    "status": a.status
                }
                for a in agendamentos
            ]
        }

    finally:
        db.close()


@app.delete("/agendamento/{agendamento_id}")
async def cancelar_agendamento(agendamento_id: int):
    """Cancela um agendamento pendente"""
    db = SessionLocal()
    try:
        agendamento = db.query(Agendamento).filter(Agendamento.id == agendamento_id).first()

        if not agendamento:
            raise HTTPException(status_code=404, detail="Agendamento não encontrado")

        if agendamento.status != "pendente":
            raise HTTPException(
                status_code=400,
                detail=f"Não é possível cancelar agendamento com status '{agendamento.status}'"
            )

        db.delete(agendamento)
        db.commit()

        return {
            "message": "Agendamento cancelado com sucesso",
            "agendamento_id": agendamento_id
        }

    finally:
        db.close()


# ====================================
# ENDPOINTS PARA ALERTAS
# ====================================

@app.get("/alertas")
async def listar_alertas(tipo: str = None, limite: int = 50):
    """Lista os alertas do sistema"""
    db = SessionLocal()
    try:
        query = db.query(Alerta)

        if tipo:
            query = query.filter(Alerta.tipo == tipo)

        alertas = query.order_by(Alerta.criado_em.desc()).limit(limite).all()

        return {
            "total": len(alertas),
            "alertas": [
                {
                    "id": a.id,
                    "tipo": a.tipo,
                    "descricao": a.descricao,
                    "criado_em": a.criado_em.isoformat()
                }
                for a in alertas
            ]
        }

    finally:
        db.close()


# ====================================
# ENDPOINTS GERAIS
# ====================================

@app.get("/make-call")
async def make_call(to_number: str, agendamento_id: int = None):
    """
    Faz uma ligação via Twilio para um número específico

    Parâmetros:
    - to_number: Número de telefone no formato internacional (+5511999999999)
    - agendamento_id: ID do agendamento (opcional)

    Exemplo: /make-call?to_number=+5511999999999&agendamento_id=1
    """
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_PHONE_NUMBER:
        raise HTTPException(
            status_code=500,
            detail="Credenciais Twilio não configuradas. Verifique o arquivo .env"
        )

    try:
        twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        # URL do TwiML que vai iniciar o stream de áudio
        twiml_url = f"https://{SERVICE_DOMAIN}/twiml"
        if agendamento_id:
            twiml_url += f"?agendamento_id={agendamento_id}"

        print(f"\n📞 Iniciando ligação...")
        print(f"   Para: {to_number}")
        print(f"   De: {TWILIO_PHONE_NUMBER}")
        print(f"   TwiML: {twiml_url}")

        # Faz a ligação
        call = twilio_client.calls.create(
            url=twiml_url,
            to=to_number,
            from_=TWILIO_PHONE_NUMBER
        )

        print(f"   ✓ Ligação iniciada - SID: {call.sid}\n")

        # Atualiza status do agendamento se fornecido
        if agendamento_id:
            db = SessionLocal()
            try:
                agendamento = db.query(Agendamento).filter(Agendamento.id == agendamento_id).first()
                if agendamento:
                    agendamento.status = "ligado"
                    db.commit()
            finally:
                db.close()

        return {
            "success": True,
            "message": "Ligação iniciada com sucesso",
            "call_sid": call.sid,
            "to": to_number,
            "from": TWILIO_PHONE_NUMBER,
            "status": call.status
        }

    except Exception as e:
        print(f"   ✗ Erro ao fazer ligação: {e}\n")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao fazer ligação: {str(e)}"
        )


@app.post("/twiml")
@app.get("/twiml")
async def twiml_endpoint(agendamento_id: int = None):
    """
    Retorna as instruções TwiML para o Twilio conectar ao WebSocket
    Este endpoint é chamado automaticamente pelo Twilio quando a ligação é atendida
    """
    print(f"📋 TwiML solicitado para agendamento #{agendamento_id if agendamento_id else 'N/A'}")

    # URL do WebSocket onde o voice_service está rodando
    # Normalmente o voice_service roda em uma porta diferente (8080)
    # e precisa estar exposto via ngrok ou similar
    voice_service_domain = os.getenv("VOICE_SERVICE_DOMAIN", SERVICE_DOMAIN)
    ws_url = f"wss://{voice_service_domain}/media-stream"

    if agendamento_id:
        ws_url += f"?agendamento_id={agendamento_id}"

    xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect>
        <Stream url="{ws_url}" />
    </Connect>
</Response>"""

    return Response(content=xml_response, media_type="application/xml")


@app.get("/")
async def root():
    """Endpoint raiz com informações sobre a API"""
    return {
        "servico": "EVA - Sistema de Lembretes de Medicação",
        "versao": "2.0",
        "endpoints": {
            "Idosos": {
                "POST /idosos": "Cria um novo idoso",
                "GET /idosos": "Lista todos os idosos",
                "GET /idosos/{id}": "Obtém um idoso específico",
                "PUT /idosos/{id}": "Atualiza um idoso",
                "DELETE /idosos/{id}": "Exclui um idoso"
            },
            "Familiares": {
                "POST /familiares": "Cria um novo familiar",
                "GET /familiares": "Lista todos os familiares",
                "PUT /familiares/{id}": "Atualiza um familiar",
                "DELETE /familiares/{id}": "Exclui um familiar"
            },
            "Agendamentos": {
                "POST /agendar": "Cria um novo agendamento",
                "GET /agendamentos": "Lista todos os agendamentos",
                "DELETE /agendamento/{id}": "Cancela um agendamento pendente"
            },
            "Alertas": {
                "GET /alertas": "Lista alertas do sistema"
            },
            "Ligações": {
                "GET /make-call?to_number=+5511999999999": "Faz uma ligação imediata",
                "GET /twiml": "Endpoint TwiML (usado pelo Twilio)"
            }
        }
    }


@app.on_event("startup")
async def startup():
    """Inicializa o scheduler quando a aplicação inicia"""
    print("=" * 60)
    print("🚀 INICIANDO SCHEDULER DA EVA")
    print("=" * 60)
    print(f"Verificação: a cada 30 segundos")
    print(f"Domínio: {SERVICE_DOMAIN}")
    print("=" * 60 + "\n")

    # Adiciona a tarefa de verificação que roda a cada 30 segundos
    scheduler.add_job(verificar_e_disparar, "interval", seconds=30)
    scheduler.start()

    print("✓ Scheduler ativo e monitorando agendamentos\n")


@app.on_event("shutdown")
async def shutdown():
    """Para o scheduler quando a aplicação encerra"""
    scheduler.shutdown()
    print("\n🛑 Scheduler encerrado")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)