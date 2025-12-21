import os
import json
import base64
import uvicorn
import asyncio
import time

try:
    import audioop
except ImportError:
    import audioop_lts as audioop

from google import genai
from google.genai import types
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import Response
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

# --- Configurações ---
PORT = int(os.getenv("PORT", "8080"))
SERVICE_DOMAIN = os.getenv("SERVICE_DOMAIN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Cliente Gemini
client = genai.Client(api_key=GOOGLE_API_KEY)

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

app = FastAPI()


@app.get("/make-call")
async def make_call(to_number: str):
    """Endpoint para disparar a ligação"""
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
    """Instrução para o Twilio abrir o canal de voz"""
    print("📋 TwiML solicitado")
    xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Connect>
            <Stream url="wss://{SERVICE_DOMAIN}/media-stream" />
        </Connect>
    </Response>"""
    return Response(content=xml_response, media_type="text/xml")


async def send_audio_to_twilio(websocket: WebSocket, audio_data: bytes, stream_sid: str):
    """Envia áudio para o Twilio no formato correto"""
    try:
        if not audio_data or len(audio_data) == 0:
            print("⚠ [TWILIO] Áudio vazio recebido")
            return

        # Gemini retorna áudio em 24kHz PCM 16-bit, converter para 8kHz
        audio_8khz = audioop.ratecv(audio_data, 2, 1, 24000, 8000, None)[0]

        # Converte para u-law (formato do Twilio)
        audio_ulaw = audioop.lin2ulaw(audio_8khz, 2)

        # Envia em chunks de 20ms (160 bytes)
        chunk_size = 160
        chunks_sent = 0

        for i in range(0, len(audio_ulaw), chunk_size):
            chunk = audio_ulaw[i:i + chunk_size]
            payload = base64.b64encode(chunk).decode('utf-8')

            await websocket.send_text(json.dumps({
                "event": "media",
                "streamSid": stream_sid,
                "media": {
                    "payload": payload
                }
            }))
            chunks_sent += 1
            await asyncio.sleep(0.02)

        return chunks_sent

    except Exception as e:
        print(f"✗ [TWILIO] Erro ao enviar áudio: {e}")
        import traceback
        traceback.print_exc()
        return 0


def detect_speech(audio_pcm: bytes, threshold: int = 500) -> bool:
    """Detecta se há fala no áudio"""
    try:
        rms = audioop.rms(audio_pcm, 2)
        return rms > threshold
    except Exception:
        return False


async def gemini_live_session(twilio_ws: WebSocket, stream_sid: str):
    """Gerencia a sessão Live API com o Gemini"""

    print("\n" + "=" * 60)
    print("🤖 INICIANDO SESSÃO GEMINI")
    print("=" * 60)

    config = {
        "response_modalities": ["AUDIO"],
        "system_instruction": SYSTEM_PROMPT,
        "speech_config": {
            "voice_config": {
                "prebuilt_voice_config": {
                    "voice_name": "Aoede"
                }
            }
        }
    }

    try:
        async with client.aio.live.connect(model=MODEL_ID, config=config) as session:
            print("✓ [GEMINI] Conectado ao Live API")

            # IMPORTANTE: Envia mensagem inicial para Eva se apresentar
            await asyncio.sleep(0.5)

            greeting = "Olá! Aqui é a Eva. Como você está hoje?"
            print(f"💬 [SYSTEM] Enviando saudação inicial: '{greeting}'")

            await session.send(
                input=greeting,
                end_of_turn=True
            )
            print("✓ [SYSTEM] Saudação enviada\n")

            audio_buffer = bytearray()
            BUFFER_SIZE = 3200  # 200ms at 16kHz * 2 bytes

            is_speaking = False
            last_speech_time = 0
            SILENCE_THRESHOLD = 1.5

            eva_is_speaking = False
            user_turn_ended = False  # Flag para saber quando usuário terminou de falar

            async def receive_from_twilio():
                nonlocal audio_buffer, is_speaking, last_speech_time, eva_is_speaking, user_turn_ended

                print("👂 [TWILIO→GEMINI] Thread de recepção iniciada")

                try:
                    packet_count = 0
                    while True:
                        data = await twilio_ws.receive_text()
                        packet = json.loads(data)
                        event = packet.get('event')

                        if event == 'media':
                            packet_count += 1
                            if packet_count % 200 == 0:
                                print(f"📦 [TWILIO→GEMINI] {packet_count} pacotes recebidos...")

                            payload = base64.b64decode(packet['media']['payload'])
                            audio_pcm = audioop.ulaw2lin(payload, 2)

                            # Converte de 8kHz para 16kHz
                            audio_16khz = audioop.ratecv(audio_pcm, 2, 1, 8000, 16000, None)[0]
                            audio_buffer.extend(audio_16khz)

                            if len(audio_buffer) >= BUFFER_SIZE:
                                audio_chunk = bytes(audio_buffer)
                                audio_buffer.clear()

                                rms = audioop.rms(audio_chunk, 2)

                                # Só processa áudio do usuário se Eva NÃO estiver falando
                                if not eva_is_speaking:
                                    if detect_speech(audio_chunk, threshold=400):
                                        current_time = time.time()

                                        if not is_speaking:
                                            print(f"🎤 [USER] Iniciou fala (RMS: {rms})")
                                            is_speaking = True
                                            user_turn_ended = False

                                        last_speech_time = current_time

                                        try:
                                            await session.send_realtime_input(
                                                audio=types.Blob(
                                                    data=audio_chunk,
                                                    mime_type='audio/pcm;rate=16000'
                                                )
                                            )
                                        except Exception as e:
                                            print(f"✗ Erro ao enviar áudio: {e}")

                                    elif is_speaking:
                                        current_time = time.time()
                                        silence_duration = current_time - last_speech_time

                                        if silence_duration > SILENCE_THRESHOLD and not user_turn_ended:
                                            print(f"🔇 [USER] Fim do turno (silêncio: {silence_duration:.1f}s)")
                                            is_speaking = False
                                            user_turn_ended = True
                                            audio_buffer.clear()

                                            # Sinaliza fim do turno explicitamente
                                            print("   ↳ Sinalizando fim do turno para Gemini...")
                                            try:
                                                # Envia um pequeno delay para garantir que todo áudio foi processado
                                                await asyncio.sleep(0.1)
                                            except Exception as e:
                                                print(f"   ✗ Erro ao sinalizar fim: {e}")

                        elif event == 'stop':
                            print("🛑 [TWILIO] Evento STOP recebido")
                            break

                except Exception as e:
                    print(f"✗ [TWILIO→GEMINI] ERRO: {e}")
                    import traceback
                    traceback.print_exc()

            async def receive_from_gemini():
                nonlocal eva_is_speaking, user_turn_ended

                print("👂 [GEMINI→TWILIO] Thread de recepção iniciada\n")

                try:
                    response_count = 0
                    audio_accumulator = bytearray()  # Acumula chunks de áudio

                    async for response in session.receive():
                        # Log do setup_complete
                        if response.setup_complete:
                            print("✓ [GEMINI] Setup completo!")
                            continue

                        # Processa resposta de áudio
                        if response.server_content:
                            content = response.server_content

                            if content.model_turn:
                                if content.model_turn.parts:
                                    for idx, part in enumerate(content.model_turn.parts):
                                        if part.inline_data:
                                            mime = part.inline_data.mime_type

                                            if mime.startswith("audio/"):
                                                # Acumula o áudio ao invés de enviar imediatamente
                                                audio_accumulator.extend(part.inline_data.data)

                                                if not eva_is_speaking:
                                                    response_count += 1
                                                    print(f"\n🔊 [EVA] Resposta #{response_count} - iniciando fala")
                                                    eva_is_speaking = True

                                        if part.text:
                                            print(f"💬 [EVA] Texto: {part.text}")

                            # Quando o turno da Eva terminar, envia todo o áudio acumulado
                            if content.turn_complete:
                                if len(audio_accumulator) > 0:
                                    total_bytes = len(audio_accumulator)
                                    print(f"📤 [EVA] Enviando áudio completo ({total_bytes} bytes)...")

                                    chunks = await send_audio_to_twilio(
                                        twilio_ws,
                                        bytes(audio_accumulator),
                                        stream_sid
                                    )

                                    print(f"✓ [EVA] Áudio enviado ({chunks} chunks)")
                                    audio_accumulator.clear()

                                print("✓ [EVA] Turno completo\n")
                                eva_is_speaking = False
                                user_turn_ended = False

                            if content.interrupted:
                                print("⚠ [EVA] Interrompida")
                                eva_is_speaking = False
                                audio_accumulator.clear()

                except Exception as e:
                    print(f"✗ [GEMINI→TWILIO] ERRO: {e}")
                    import traceback
                    traceback.print_exc()

            print("🚀 Iniciando loops de processamento...\n")
            await asyncio.gather(
                receive_from_twilio(),
                receive_from_gemini(),
                return_exceptions=True
            )

    except Exception as e:
        print(f"✗ [GEMINI] Erro na sessão: {e}")
        import traceback
        traceback.print_exc()


@app.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    await websocket.accept()
    print("\n" + "=" * 60)
    print("🔌 NOVA CONEXÃO WEBSOCKET")
    print("=" * 60)

    stream_sid = None

    try:
        while True:
            data = await websocket.receive_text()
            packet = json.loads(data)
            event = packet.get('event')

            if event == 'connected':
                print("✓ [WEBSOCKET] Conectado ao Twilio")

            elif event == 'start':
                stream_sid = packet['start']['streamSid']
                print(f"✓ [WEBSOCKET] Stream ID: {stream_sid}")
                print(f"✓ [WEBSOCKET] Iniciando sessão Gemini...\n")
                await gemini_live_session(websocket, stream_sid)
                break

    except WebSocketDisconnect:
        print("\n✓ [WEBSOCKET] Desconectado")
    except Exception as e:
        print(f"\n✗ [WEBSOCKET] Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 EVA - Assistente de Voz")
    print("=" * 60)
    print(f"Porta: {PORT}")
    print(f"Domínio: {SERVICE_DOMAIN}")
    print("=" * 60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=PORT)