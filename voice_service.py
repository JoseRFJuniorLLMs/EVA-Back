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
from dotenv import load_dotenv
from database import SessionLocal, Agendamento, Alerta

load_dotenv()

# --- Configurações ---
PORT = int(os.getenv("PORT", "8080"))
SERVICE_DOMAIN = os.getenv("SERVICE_DOMAIN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Cliente Gemini
client = genai.Client(api_key=GOOGLE_API_KEY)

MODEL_ID = "gemini-2.5-flash-native-audio-preview-12-2025"

app = FastAPI()


def criar_prompt_personalizado(agendamento_id: int) -> str:
    """Busca os dados do agendamento e cria um prompt personalizado para a Eva"""
    db = SessionLocal()
    try:
        agendamento = db.query(Agendamento).filter(Agendamento.id == agendamento_id).first()

        if not agendamento:
            return """Você é a Eva, uma assistente pessoal muito gentil, paciente e carinhosa que cuida de idosos.
Sua voz deve ser doce e calma. Fale de forma simples e natural."""

        nome = agendamento.nome_idoso
        remedios = agendamento.remedios

        prompt = f"""Você é a Eva, uma assistente pessoal muito gentil, paciente e carinhosa que cuida de idosos.
Sua voz deve ser doce e calma. Fale de forma simples e natural, como se estivesse conversando com um amigo querido.

IMPORTANTE: 
- Você está ligando para {nome}
- Você precisa lembrá-lo(a) de tomar os seguintes remédios: {remedios}
- Responda SEMPRE de forma direta e natural
- NÃO pense alto, NÃO explique seu raciocínio
- Seja breve e vá direto ao ponto (máximo 2-3 frases por resposta)
- Use linguagem simples e calorosa
- Pergunte se {nome} já tomou os remédios
- Se {nome} disser que não está se sentindo bem, pergunte o que está sentindo
- Espere o usuário falar antes de responder novamente

PROTOCOLO DE EMERGÊNCIA:
- Se {nome} mencionar dor forte, tontura, falta de ar, dor no peito ou qualquer sintoma grave, você deve:
  1. Manter a calma e tranquilizar a pessoa
  2. Perguntar se há alguém por perto que possa ajudar
  3. Avisar que você vai notificar a família imediatamente
  4. NÃO encerrar a ligação até ter certeza de que há ajuda a caminho
"""

        return prompt

    finally:
        db.close()


@app.post("/twiml")
async def twiml_endpoint(agendamento_id: int = None):
    """Instrução para o Twilio abrir o canal de voz"""
    print(f"📋 TwiML solicitado para agendamento #{agendamento_id}")

    # Passa o agendamento_id para o WebSocket via query string
    ws_url = f"wss://{SERVICE_DOMAIN}/media-stream?agendamento_id={agendamento_id}" if agendamento_id else f"wss://{SERVICE_DOMAIN}/media-stream"

    xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Connect>
            <Stream url="{ws_url}" />
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


def registrar_alerta(tipo: str, descricao: str):
    """Registra um alerta no banco de dados"""
    db = SessionLocal()
    try:
        novo_alerta = Alerta(tipo=tipo, descricao=descricao)
        db.add(novo_alerta)
        db.commit()
        print(f"🚨 ALERTA REGISTRADO: {tipo} - {descricao}")
    finally:
        db.close()


def analisar_conversa_para_alertas(texto: str, nome_idoso: str, agendamento_id: int):
    """Analisa o texto da conversa procurando por sinais de emergência"""
    palavras_alerta = [
        "dor", "mal", "tontura", "tonto", "zonzo", "peito", "coração",
        "falta de ar", "respirar", "cabeça", "ajuda", "socorro",
        "fraco", "fraca", "cansado", "cansada"
    ]

    texto_lower = texto.lower()

    for palavra in palavras_alerta:
        if palavra in texto_lower:
            registrar_alerta(
                tipo="PASSA_MAL",
                descricao=f"{nome_idoso} (Agendamento #{agendamento_id}) mencionou: '{texto}'"
            )
            break


async def gemini_live_session(twilio_ws: WebSocket, stream_sid: str, agendamento_id: int = None):
    """Gerencia a sessão Live API com o Gemini"""

    print("\n" + "=" * 60)
    print(f"🤖 INICIANDO SESSÃO GEMINI - Agendamento #{agendamento_id}")
    print("=" * 60)

    # Busca informações do agendamento
    db = SessionLocal()
    agendamento = None
    nome_idoso = "você"

    if agendamento_id:
        agendamento = db.query(Agendamento).filter(Agendamento.id == agendamento_id).first()
        if agendamento:
            nome_idoso = agendamento.nome_idoso
            print(f"👤 Paciente: {nome_idoso}")
            print(f"💊 Remédios: {agendamento.remedios}")

    db.close()

    system_prompt = criar_prompt_personalizado(agendamento_id) if agendamento_id else """Você é a Eva, uma assistente pessoal muito gentil, paciente e carinhosa que cuida de idosos.
Sua voz deve ser doce e calma. Fale de forma simples e natural."""

    config = {
        "response_modalities": ["AUDIO"],
        "system_instruction": system_prompt,
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

            # Saudação inicial personalizada
            await asyncio.sleep(0.5)

            greeting = f"Olá {nome_idoso}! Aqui é a Eva. Como você está hoje?"
            print(f"💬 [SYSTEM] Enviando saudação inicial: '{greeting}'")

            await session.send(
                input=greeting,
                end_of_turn=True
            )
            print("✓ [SYSTEM] Saudação enviada\n")

            audio_buffer = bytearray()
            BUFFER_SIZE = 3200

            is_speaking = False
            last_speech_time = 0
            SILENCE_THRESHOLD = 1.5

            eva_is_speaking = False
            user_turn_ended = False

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

                                            print("   ↳ Sinalizando fim do turno para Gemini...")
                                            try:
                                                await asyncio.sleep(0.1)
                                            except Exception as e:
                                                print(f"   ✗ Erro ao sinalizar fim: {e}")

                        elif event == 'stop':
                            print("🛑 [TWILIO] Evento STOP recebido")

                            # Atualiza status do agendamento
                            if agendamento_id:
                                db = SessionLocal()
                                try:
                                    agend = db.query(Agendamento).filter(Agendamento.id == agendamento_id).first()
                                    if agend:
                                        agend.status = "concluido"
                                        db.commit()
                                        print(f"✓ Agendamento #{agendamento_id} marcado como concluído")
                                finally:
                                    db.close()

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
                    audio_accumulator = bytearray()

                    async for response in session.receive():
                        if response.setup_complete:
                            print("✓ [GEMINI] Setup completo!")
                            continue

                        if response.server_content:
                            content = response.server_content

                            if content.model_turn:
                                if content.model_turn.parts:
                                    for idx, part in enumerate(content.model_turn.parts):
                                        if part.inline_data:
                                            mime = part.inline_data.mime_type

                                            if mime.startswith("audio/"):
                                                audio_accumulator.extend(part.inline_data.data)

                                                if not eva_is_speaking:
                                                    response_count += 1
                                                    print(f"\n📊 [EVA] Resposta #{response_count} - iniciando fala")
                                                    eva_is_speaking = True

                                        if part.text:
                                            print(f"💬 [EVA] Texto: {part.text}")

                                            # Analisa o texto para alertas
                                            if agendamento_id:
                                                analisar_conversa_para_alertas(part.text, nome_idoso, agendamento_id)

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
async def handle_media_stream(websocket: WebSocket, agendamento_id: int = None):
    await websocket.accept()
    print("\n" + "=" * 60)
    print("🔌 NOVA CONEXÃO WEBSOCKET")
    if agendamento_id:
        print(f"📋 Agendamento: #{agendamento_id}")
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
                await gemini_live_session(websocket, stream_sid, agendamento_id)
                break

    except WebSocketDisconnect:
        print("\n✓ [WEBSOCKET] Desconectado")

        # Se desconectou sem concluir, marca como "nao_atendeu"
        if agendamento_id:
            db = SessionLocal()
            try:
                agend = db.query(Agendamento).filter(Agendamento.id == agendamento_id).first()
                if agend and agend.status == "ligado":
                    agend.status = "nao_atendeu"
                    db.commit()

                    registrar_alerta(
                        tipo="NAO_ATENDEU",
                        descricao=f"{agend.nome_idoso} não atendeu ou desligou a chamada"
                    )
            finally:
                db.close()

    except Exception as e:
        print(f"\n✗ [WEBSOCKET] Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 EVA - Serviço de Voz")
    print("=" * 60)
    print(f"Porta: {PORT}")
    print(f"Domínio: {SERVICE_DOMAIN}")
    print("=" * 60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=PORT)