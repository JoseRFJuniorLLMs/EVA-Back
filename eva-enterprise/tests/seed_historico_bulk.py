
import sys
import os
import random
import json
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select

# Fix sys.path to include 'eva-enterprise' directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir) # eva-enterprise
sys.path.append(parent_dir)

from database.connection import AsyncSessionLocal, DATABASE_URL, engine, Base
from database.models import Idoso, HistoricoLigacao, Agendamento

async def seed_historico(num_entries_per_idoso=10):
    print(f"DEBUG: DATABASE_URL logada: {DATABASE_URL}")
    print("DEBUG: GarantindoSchema completo...")
    
    # Criar tabelas (garantia)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("DEBUG: Iniciando inserção...")
    async with AsyncSessionLocal() as session:
        try:
            # Buscar Idosos
            result = await session.execute(select(Idoso))
            idosos = result.scalars().all()
            
            if not idosos:
                print("ERRO: Nenhum idoso encontrado. Rode seed_idosos.py primeiro.")
                return

            print(f"Encontrados {len(idosos)} idosos para gerar histórico.")

            moods = [
                ("feliz", "Idoso relatou estar contente com a visita dos netos."),
                ("triste", "Mencionou saudade de familiares distantes."),
                ("neutro", "Conversa padrão sobre rotina e medição."),
                ("ansioso", "Preocupação com consulta médica agendada."),
                ("irritado", "Reclamou de dores nas costas e dificuldade para dormir."),
                ("confuso", "Não lembrava bem do horário do remédio."),
                ("animado", "Estava ouvindo música antiga e se sentindo bem.")
            ]
            
            voices = ["Puck", "Charon", "Kore", "Fenrir", "Aoede"]
            qualities = ["excelente", "boa", "regular", "ruim"]

            count = 0
            
            for idoso in idosos:
                # Gerar X entradas para cada idoso
                for _ in range(num_entries_per_idoso):
                    days_ago = random.randint(0, 60)
                    dt_agendada = datetime.now() - timedelta(days=days_ago, hours=random.randint(8, 18))
                    
                    # 1. CRIAR AGENDAMENTO (Necessário para a FK)
                    agendamento = Agendamento(
                        idoso_id=idoso.id,
                        tipo=random.choice(['lembrete_medicamento', 'check_bem_estar']),
                        data_hora_agendada=dt_agendada,
                        data_hora_realizada=dt_agendada + timedelta(seconds=random.randint(10, 60)),
                        status='concluido',
                        tentativas_realizadas=1,
                        dados_tarefa={"medicamento": "Losartana", "dosagem": "50mg"},
                        criado_por="system_seed"
                    )
                    session.add(agendamento)
                    await session.flush() # Para gerar o ID do agendamento

                    # 2. CRIAR HISTÓRICO (Com todos os campos do SQL)
                    mood, context = random.choice(moods)
                    duration = random.randint(60, 600)
                    start_call = agendamento.data_hora_realizada
                    end_call = start_call + timedelta(seconds=duration)
                    success = random.random() > 0.1 # 90% sucesso

                    historico = HistoricoLigacao(
                        agendamento_id=agendamento.id,
                        idoso_id=idoso.id,
                        
                        # IDs Técnicos
                        twilio_call_sid=f"CA{random.randint(100000,999999)}seed",
                        stream_sid=f"MX{random.randint(100000,999999)}seed",
                        
                        # Timestamps
                        inicio_chamada=start_call,
                        fim_chamada=end_call,
                        duracao_segundos=duration,
                        
                        # Config
                        modelo_utilizado="gemini-2.0-flash-exp",
                        voice_name=random.choice(voices),
                        config_snapshot={"temperature": 0.8},
                        
                        # Qualidade
                        qualidade_audio=random.choice(qualities),
                        interrupcoes_detectadas=random.randint(0, 5),
                        latencia_media_ms=random.randint(200, 800),
                        packets_perdidos=random.randint(0, 50),
                        vad_false_positives=random.randint(0, 3),
                        
                        # Resultado
                        tarefa_concluida=success,
                        objetivo_alcancado=success,
                        motivo_falha=None if success else "Idoso não atendeu ou não confirmou",
                        
                        # Conteúdo
                        transcricao_completa=f"[SEED] Transcrição simulada de conversa com {idoso.nome}. {context}",
                        transcricao_resumo=context if success else "Não houve contato efetivo.",
                        sentimento_geral=mood,
                        sentimento_intensidade=random.randint(1, 10),
                        acoes_registradas=[{"acao": "confirm_medication", "timestamp": str(start_call)}],
                        
                        # FinOps
                        tokens_gemini=random.randint(500, 5000),
                        minutos_twilio=int(duration/60) + 1,
                        
                        criado_em=start_call
                    )
                    session.add(historico)
                    count += 1

            await session.commit()
            print(f"✅ SUCESSO! Inseridos {count} agendamentos e históricos completos.")

        except Exception as e:
            await session.rollback()
            print(f"❌ ERRO CRÍTICO: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed_historico())
