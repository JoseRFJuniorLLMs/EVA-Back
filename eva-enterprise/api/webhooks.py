from datetime import datetime, timedelta
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from engine.gemini_session import GeminiSession
from brain.context_builder import ContextBuilder
from services.telemetry import TelemetryService
from database.connection import SessionLocal
from database.repositories.agendamento_repo import AgendamentoRepository
from database.repositories.historico_repo import HistoricoRepository
from handlers.alerts import AlertsHandler

import json
import traceback

router = APIRouter()


@router.websocket("/media-stream")
async def handle_media_stream_legacy(websocket: WebSocket, agendamento_id: int = None):
    """Endpoint legado para compatibilidade"""
    await handle_media_stream(websocket, str(agendamento_id) if agendamento_id else None)


from engine.twilio_reconnection import TwilioStreamReconnection

@router.websocket("/media-stream/{agendamento_id}")
async def handle_media_stream(websocket: WebSocket, agendamento_id: str = None):
    """
    Handler principal do WebSocket para stream de mídia Twilio.
    Integra com Gemini, telemetria e sistema de retry.
    """
    await websocket.accept()
    print("\n" + "=" * 60)
    print("🔌 NOVA CONEXÃO WEBSOCKET")
    if agendamento_id:
        print(f"📋 Agendamento: #{agendamento_id}")
    print("=" * 60)
    
    # Variáveis de contexto
    context = None
    stream_sid = None
    session = None
    ligacao_id = None
    db = None
    
    # Gerenciador de reconexão
    reconnection = TwilioStreamReconnection()
    
    try:
        # Inicia monitoramento
        async def on_timeout():
            print("⚠️ [RECONNECTION] Tentando recuperar conexão...")
            # Aqui poderia ter lógica de reconexão mais complexa
            
        await reconnection.start_watchdog(on_timeout)
        
        # 1. Busca contexto da ligação
        context_builder = ContextBuilder()
        if agendamento_id:
            context = await context_builder.build_call_context(int(agendamento_id))
        else:
            context = {'retry_config': {'current_retry': 0, 'max_retries': 3, 'retry_interval': 15, 'escalation_policy': 'alert_family'}}
        
        # 2. Aguarda evento 'start' do Twilio
        while True:
            data = await websocket.receive_text()
            packet = json.loads(data)
            event = packet.get('event')
            
            # Notifica watchdog
            reconnection.mark_packet_received()

            if event == 'connected':
                print("✓ [WEBSOCKET] Conectado ao Twilio")
                reconnection.mark_connected()

            elif event == 'start':
                stream_sid = packet['start']['streamSid']
                print(f"✓ [WEBSOCKET] Stream ID: {stream_sid}")
                
                # 3. Cria registro no histórico
                db = SessionLocal()
                historico_repo = HistoricoRepository(db)
                ligacao_id = await historico_repo.create({
                    'agendamento_id': agendamento_id,
                    'idoso_id': context.get('metadata', {}).get('idoso_id'),
                    'call_sid': stream_sid,
                    'status': 'em_andamento',
                    'inicio': datetime.now()
                })
                
                # Adiciona ligacao_id ao contexto
                if 'metadata' not in context:
                    context['metadata'] = {}
                context['metadata']['ligacao_id'] = ligacao_id
                
                # 4. Inicia sessão Gemini
                session = GeminiSession(websocket, stream_sid, int(agendamento_id) if agendamento_id else None, context)
                await session.start()
                break
        
        # 5. Pós-processamento (após sessão encerrar normalmente)
        if session and ligacao_id:
            telemetry = TelemetryService()
            
            # Coleta métricas da sessão
            interruptions = getattr(session, 'interruptions_count', 0)
            avg_latency = getattr(session, 'avg_latency', 0)
            vad_false_positives = 0
            
            if hasattr(session, 'audio_processor') and session.audio_processor:
                vad_false_positives = getattr(session.audio_processor, 'vad_false_positives', 0)
            
            await telemetry.log_call_telemetry(
                ligacao_id=str(ligacao_id),
                qualidade_audio='boa',
                interrupcoes=interruptions,
                latencia_media_ms=avg_latency,
                vad_false_positives=vad_false_positives
            )
            
            # Atualiza status do agendamento
            if agendamento_id:
                agendamento_repo = AgendamentoRepository(db)
                task_completed = getattr(session, 'task_completed', False)
                new_status = 'concluido' if task_completed else 'falhou'
                await agendamento_repo.update_status(int(agendamento_id), new_status)
                print(f"✓ [AGENDAMENTO] Status atualizado para: {new_status}")

    except WebSocketDisconnect:
        print("\n✓ [WEBSOCKET] Desconectado")
        reconnection.mark_disconnected()
        
    except Exception as e:
        print(f"\n✗ [WEBSOCKET] Erro: {e}")
        traceback.print_exc()
        
        # Lógica de Re-tentativa
        if context and 'retry_config' in context:
            retry_config = context['retry_config']
            current_retry = retry_config.get('current_retry', 0)
            max_retries = retry_config.get('max_retries', 3)
            
            if agendamento_id:
                try:
                    if db is None:
                        db = SessionLocal()
                    agendamento_repo = AgendamentoRepository(db)
                    
                    if current_retry < max_retries:
                        # Agenda nova tentativa
                        next_attempt = datetime.now() + timedelta(minutes=retry_config.get('retry_interval', 15))
                        await agendamento_repo.update(int(agendamento_id), {
                            'tentativas_realizadas': current_retry + 1,
                            'proxima_tentativa': next_attempt,
                            'status': 'aguardando_retry'
                        })
                        print(f"🔄 Tentativa {current_retry+1}/{max_retries} agendada para {next_attempt}")
                    else:
                        # Esgotou tentativas → Escalona
                        if retry_config.get('escalation_policy') == 'alert_family':
                            idoso_nome = context.get('metadata', {}).get('idoso_nome', 'idoso')
                            await alert_family(
                                motivo=f"Não foi possível contatar {idoso_nome} após {max_retries} tentativas",
                                urgencia='alta',
                                call_context=context.get('metadata', {})
                            )
                        
                        await agendamento_repo.update_status(int(agendamento_id), 'falhou_definitivamente')
                        print(f"❌ [AGENDAMENTO] Falhou definitivamente após {max_retries} tentativas")
                except Exception as retry_error:
                    print(f"✗ [RETRY] Erro ao processar retry: {retry_error}")
    
    finally:
        # Para watchdog
        reconnection.stop_watchdog()
        
        # Finaliza registro no histórico
        if ligacao_id and db:
            try:
                historico_repo = HistoricoRepository(db)
                await historico_repo.update(ligacao_id, {
                    'fim': datetime.now(),
                    'status': 'finalizado'
                })
            except Exception as hist_error:
                print(f"✗ [HISTORICO] Erro ao finalizar: {hist_error}")
        
        # Fecha conexão com banco
        if db:
            db.close()
