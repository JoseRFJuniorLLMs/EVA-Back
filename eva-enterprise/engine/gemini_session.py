import json
import base64
import asyncio
import time
from asyncio import Lock
from fastapi import WebSocket
from google import genai
from google.genai import types
from config.settings import settings
from .audio_processor import AudioProcessor
from handlers.alerts import AlertsHandler
from handlers.sentiment import SentimentHandler  # Placeholder
from handlers.medication import confirm_medication
from brain.context_builder import ContextBuilder
from database.connection import SessionLocal
from database.repositories.agendamento_repo import AgendamentoRepository


class GeminiSession:
    def __init__(self, websocket: WebSocket, stream_sid: str, agendamento_id: int = None, context: dict = None):
        self.websocket = websocket
        self.stream_sid = stream_sid
        self.agendamento_id = agendamento_id
        self.context = context or {}
        self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        self.alerts_handler = AlertsHandler()
        
        # Controle de sessão e locks
        self.function_lock = Lock()
        self.session_active = True
        self.current_session_handle = None
        
        # Inicializa AudioProcessor (sem sessão por enquanto)
        self.audio_processor = AudioProcessor(
            context=self.context,
            on_turn_complete=self.on_turn_complete
        )
        
        # State Restoration (Session Resumption)
        checkpoint = self.context.get('session_resumption', {}).get('checkpoint_state', {})
        if checkpoint:
            print(f"🔄 [SESSION] Restaurando estado anterior: {checkpoint}")
            self.turn_count = checkpoint.get('turno', 0)
            self.last_user_input = checkpoint.get('ultimo_user_input', "")
            self.last_model_output = checkpoint.get('ultimo_model_output', "")
            self.task_completed = checkpoint.get('task_completed', False)
            self.functions_called = checkpoint.get('functions_called', [])
        else:
            self.turn_count = 0
            self.last_user_input = ""
            self.last_model_output = ""
            self.task_completed = False
            self.functions_called = []
            
        self.interruptions_count = 0
        self.avg_latency = 0

    async def on_turn_complete(self, text: str):
        """Callback quando o AudioProcessor finaliza um turno do usuário"""
        self.turn_count += 1
        self.last_user_input = text
        print(f"📝 [TRANSCRICAO] Turno {self.turn_count}: {text}")

    async def start(self):
        print("\n" + "=" * 60)
        print(f"🤖 INICIANDO SESSÃO GEMINI - Agendamento #{self.agendamento_id}")
        if self.turn_count > 0:
            print(f"   ↳ Resumindo do turno {self.turn_count}")
        print("=" * 60)

        # Build Context/Prompt se necessário
        if not self.context:
            context_builder = ContextBuilder()
            self.context = await context_builder.build_call_context(self.agendamento_id)
        
        system_prompt = self.context.get('system_prompt')
        
        # Initial Greeting (apenas se nova sessão)
        greeting = None
        if self.turn_count == 0:
            context_builder = ContextBuilder()
            greeting = context_builder.get_initial_greeting(self.agendamento_id)

        # Configuração base
        config = {
            "response_modalities": ["AUDIO"],
            "system_instruction": system_prompt,
            "speech_config": {
                "voice_config": {
                    "prebuilt_voice_config": {
                        "voice_name": self.context.get('voice_config', {}).get('voice_name', 'Aoede')
                    }
                }
            },
            "session_resumption": {
                "transparent": True,
                "handle": self.context.get('session_resumption', {}).get('previous_handle')
            }
        }
        
        if self.context.get('functions'):
            config["tools"] = self._format_functions_for_gemini()

        try:
            async with self.client.aio.live.connect(
                model=self.context.get('model_config', {}).get('model_id', settings.MODEL_ID), 
                config=config
            ) as session:
                print("✓ [GEMINI] Conectado ao Live API")
                
                # Injeta sessão no AudioProcessor
                self.audio_processor.set_session(session)
                
                # Envia saudação apenas se for inicio
                if greeting:
                    await asyncio.sleep(0.5)
                    print(f"💬 [SYSTEM] Enviando saudação inicial")
                    await session.send(input=greeting, end_of_turn=True)

                await asyncio.gather(
                    self.receive_from_twilio(session),
                    self.receive_from_gemini(session),
                    return_exceptions=True
                )

        except Exception as e:
            print(f"✗ [GEMINI] Erro na sessão: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.session_active = False

    def _format_functions_for_gemini(self) -> list:
        """Converte functions do contexto para formato do Gemini"""
        gemini_tools = []
        for func in self.context.get('functions', []):
            gemini_tools.append({
                "function_declarations": [{
                    "name": func['nome'],
                    "description": func['descricao'],
                    "parameters": func['parametros']
                }]
            })
        return gemini_tools
    
    def _get_function_handler(self, function_name: str):
        """Retorna o handler para a função especificada"""
        handlers = {
            'confirm_medication': confirm_medication,
            'alert_family': self.alerts_handler.send_family_alert,
        }
        return handlers.get(function_name)

    async def _handle_function_call(self, tool_call: dict) -> dict:
        """Executa função com lock para prevenir race condition"""
        async with self.function_lock:
            if not self.session_active:
                return {'success': False, 'message': 'Session terminated'}
            
            # Registra chamada
            self.functions_called.append(tool_call['name'])
            
            handler = self._get_function_handler(tool_call['name'])
            if not handler:
                return {'success': False, 'message': f'Unknown function: {tool_call["name"]}'}
            
            try:
                result = await asyncio.wait_for(
                    handler(**tool_call['args'], call_context=self.context.get('metadata', {})),
                    timeout=5.0
                )
                
                # Se for confirmacao de sucesso, marca tarefa como completa
                if tool_call['name'] == 'confirm_medication' and result.get('success'):
                    self.task_completed = True
                    
                return result
            except asyncio.TimeoutError:
                return {'success': False, 'message': 'Function timeout'}
            except Exception as e:
                return {'success': False, 'message': str(e)}

    async def _save_session_handle(self, new_handle: str):
        """Salva o handle da sessão e checkpoint"""
        self.current_session_handle = new_handle
        
        if self.agendamento_id:
            db = SessionLocal()
            try:
                repo = AgendamentoRepository(db)
                await repo.update(self.agendamento_id, {
                    'gemini_session_handle': new_handle,
                    'ultima_interacao_estado': self._get_simple_checkpoint()
                })
            finally:
                db.close()
    
    def _get_simple_checkpoint(self) -> dict:
        """Retorna checkpoint do estado da conversa."""
        return {
            'turno': self.turn_count,
            'ultimo_user_input': self.last_user_input,
            'ultimo_model_output': self.last_model_output,
            'timestamp': time.time(),
            'task_completed': self.task_completed,
            'functions_called': self.functions_called
        }

    async def send_audio_to_twilio(self, audio_data: bytes):
        if not audio_data: return
        # Convert 24k -> 8k -> ulaw
        audio_8khz = self.audio_processor.ratecv_24k_to_8k(audio_data)
        audio_ulaw = self.audio_processor.lin2ulaw(audio_8khz)

        chunk_size = 160
        for i in range(0, len(audio_ulaw), chunk_size):
            chunk = audio_ulaw[i:i + chunk_size]
            payload = base64.b64encode(chunk).decode('utf-8')
            
            await self.websocket.send_text(json.dumps({
                "event": "media",
                "streamSid": self.stream_sid,
                "media": {"payload": payload}
            }))
            await asyncio.sleep(0.02)

    async def receive_from_twilio(self, session):
        """Loop de recebimento do Twilio usando AudioProcessor"""
        try:
            # Processa stream direto no AudioProcessor
            await self.audio_processor.process_twilio_stream(self.websocket)
        except Exception as e:
            print(f"✗ [TWILIO→GEMINI] ERRO: {e}")
            self.session_active = False

    async def receive_from_gemini(self, session):
        """Loop de recebimento do Gemini"""
        try:
            audio_accumulator = bytearray()
            
            async for response in session.receive():
                # Session Resumption Update
                if hasattr(response, 'session_resumption_update') and response.session_resumption_update:
                    update = response.session_resumption_update
                    if hasattr(update, 'resumable') and update.resumable and hasattr(update, 'new_handle') and update.new_handle:
                        await self._save_session_handle(update.new_handle)
                
                # Tool Call
                if hasattr(response, 'tool_call') and response.tool_call:
                    tool_call = {
                        'name': response.tool_call.name,
                        'args': dict(response.tool_call.args) if response.tool_call.args else {}
                    }
                    print(f"🔧 [FUNCTION] Chamando: {tool_call['name']}")
                    result = await self._handle_function_call(tool_call)
                    print(f"🔧 [FUNCTION] Resultado: {result}")
                    
                    await session.send(input=json.dumps(result), end_of_turn=True)
                
                # Audio/Text Content
                if response.server_content:
                    content = response.server_content
                    if content.model_turn:
                        for part in content.model_turn.parts:
                            if part.inline_data and part.inline_data.mime_type.startswith("audio/"):
                                audio_accumulator.extend(part.inline_data.data)
                            if part.text:
                                print(f"💬 [EVA] Texto: {part.text}")
                                self.last_model_output = part.text
                                self.alerts_handler.check_for_alerts(part.text, self.agendamento_id)

                    if content.turn_complete:
                        if len(audio_accumulator) > 0:
                            await self.send_audio_to_twilio(bytes(audio_accumulator))
                            audio_accumulator.clear()
                            
        except Exception as e:
            print(f"✗ [GEMINI→TWILIO] ERRO: {e}")
            self.session_active = False

