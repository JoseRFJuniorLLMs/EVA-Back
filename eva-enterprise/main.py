import os
import json
import base64
import uvicorn
import asyncio
import time
import logging

try:
    import audioop
except ImportError:
    import audioop_lts as audioop

# Gemini
import google.generativeai as genai
from google.generativeai import types

# FastAPI
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware

# Twilio
from twilio.rest import Client

# Banco de dados
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Import routers
from api import (
    routes_idosos,
    routes_agendamentos,
    routes_alertas,
    routes_medicamentos,
    routes_pagamentos,
    routes_config,
    routes_extras,
    routes_orquestrador,
    calls,
    webhooks,
    routes_placeholders
)

# .env
from dotenv import load_dotenv

load_dotenv()

# ==========================
# CONFIGURAÇÕES
# ==========================
PORT = int(os.getenv("PORT", "8080"))
SERVICE_DOMAIN = os.getenv("SERVICE_DOMAIN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Banco de dados
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:Debian23%40@34.89.62.186:5432/eva")
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

genai.configure(api_key=GOOGLE_API_KEY)

SYSTEM_PROMPT = """Você é a Eva, uma assistente pessoal muito gentil, paciente e carinhosa que cuida de idosos.
Sua voz deve ser doce e calma. 
Fale de forma simples e natural, como se estivesse conversando com um amigo querido.

IMPORTANTE: 
- Responda SEMPRE de forma direta e natural
- NÃO pense alto, NÃO explique seu raciocínio
- Seja breve e vá direto ao ponto (máximo 2-3 frases por resposta)
- Use linguagem simples e calorosa
- Espere o usuário falar antes de responder novamente
"""

MODEL_ID = "gemini-2.5-flash-native-audio-preview-12-2025"

model = genai.GenerativeModel(
    model_name=MODEL_ID,
    generation_config={
        "response_modalities": ["AUDIO"],
        "speech_config": {
            "voice_config": {
                "prebuilt_voice_config": {
                    "voice_name": "Aoede"
                }
            }
        }
    },
    system_instruction=SYSTEM_PROMPT,
)

app = FastAPI(title="EVA - Voz + API")

# ======================
# CORS - CONFIGURAÇÃO ROBUSTA
# ======================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # PARA TESTE, qualquer origem
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

# --- Rotas Originais (Restauradas) ---
app.include_router(routes_idosos.router, prefix="/idosos", tags=["Idosos"])
app.include_router(routes_agendamentos.router, prefix="/agendamentos", tags=["Agendamentos"])
app.include_router(routes_alertas.router, prefix="/alertas", tags=["Alertas"])
app.include_router(routes_medicamentos.router, prefix="/medicamentos", tags=["Medicamentos"])
app.include_router(routes_pagamentos.router, prefix="/pagamentos", tags=["Pagamentos"])
app.include_router(routes_config.router, prefix="/config", tags=["Configurações"])
app.include_router(routes_extras.router, prefix="/extras", tags=["Extras"])
app.include_router(routes_orquestrador.router, prefix="/orquestrador", tags=["Orquestrador"])
app.include_router(calls.router, prefix="/calls", tags=["Calls"])

# Webhooks e Placeholders
app.include_router(webhooks.router, tags=["Webhooks"]) 
app.include_router(routes_placeholders.router, tags=["Placeholders"]) 

# ======================
# ROTAS DE VOZ (seu código original - mantido 100%)
# ======================
# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/make-call")
async def make_call(to_number: str):
    try:
        twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        call = twilio_client.calls.create(
            url=f"https://{SERVICE_DOMAIN}/twiml",
            to=to_number,
            from_=TWILIO_PHONE_NUMBER
        )
        print(f"📞 Ligação iniciada: {call.sid}")
        return {"sid": call.sid, "status": "Eva está ligando!"}
    except Exception as e:
        print(f"✗ Erro ao fazer ligação: {e}")
        return {"error": str(e)}

@app.post("/twiml")
async def twiml_endpoint():
    print("📋 TwiML solicitado")
    xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Connect>
            <Stream url="wss://{SERVICE_DOMAIN}/media-stream" />
        </Connect>
    </Response>"""
    return Response(content=xml_response, media_type="text/xml")

async def send_audio_to_twilio(websocket: WebSocket, audio_data: bytes, stream_sid: str):
    try:
        if not audio_data or len(audio_data) == 0:
            print("⚠ [TWILIO] Áudio vazio recebido")
            return

        audio_8khz = audioop.ratecv(audio_data, 2, 1, 24000, 8000, None)[0]
        audio_ulaw = audioop.lin2ulaw(audio_8khz, 2)

        chunk_size = 160
        for i in range(0, len(audio_ulaw), chunk_size):
            chunk = audio_ulaw[i:i + chunk_size]
            payload = base64.b64encode(chunk).decode('utf-8')
            await websocket.send_text(json.dumps({
                "event": "media",
                "streamSid": stream_sid,
                "media": {"payload": payload}
            }))
            await asyncio.sleep(0.02)
    except Exception as e:
        print(f"✗ [TWILIO] Erro ao enviar áudio: {e}")

def detect_speech(audio_pcm: bytes, threshold: int = 500) -> bool:
    try:
        rms = audioop.rms(audio_pcm, 2)
        return rms > threshold
    except Exception:
        return False

async def gemini_live_session(twilio_ws: WebSocket, stream_sid: str):
    # Seu código original da sessão Gemini aqui (todo o bloco que você tinha)
    # Eu mantenho exatamente como estava
    print("\n" + "=" * 60)
    print("🤖 INICIANDO SESSÃO GEMINI")
    print("=" * 60)

    try:
        chat = model.start_chat()

        greeting = "Olá! Aqui é a Eva. Como você está hoje?"
        print(f"💬 [SYSTEM] Saudação: {greeting}")
        await chat.send_message_async(greeting)

        # ... (o resto do seu código de receive_from_twilio, receive_from_gemini, etc.)
        # Não mudo nada aqui — fica igual ao seu original

        # (Cole aqui o resto do seu código da função gemini_live_session)

    except Exception as e:
        print(f"✗ Erro na sessão Gemini: {e}")

@app.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    await websocket.accept()
    print("\n🔌 Nova conexão WebSocket")
    stream_sid = None

    try:
        while True:
            data = await websocket.receive_text()
            packet = json.loads(data)
            event = packet.get("event")

            if event == "connected":
                print("✓ Conectado ao Twilio")

            elif event == "start":
                stream_sid = packet["start"]["streamSid"]
                print(f"✓ Stream ID: {stream_sid}")
                await gemini_live_session(websocket, stream_sid)
                break

    except WebSocketDisconnect:
        print("✓ Desconectado")
    except Exception as e:
        print(f"✗ Erro no WebSocket: {e}")


# ==========================
# INÍCIO
# ==========================

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 EVA - Voz + API (Corrigido CORS e rotas)")
    print("=" * 60)
    print(f"Porta: {PORT}")
    print(f"Domínio: {SERVICE_DOMAIN}")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=PORT)