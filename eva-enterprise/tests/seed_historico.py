
import asyncio
import sys
import os
import random
from datetime import datetime, timedelta

# Adiciona o diretório raiz ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from database.connection import AsyncSessionLocal
from database.models import Idoso, HistoricoLigacao, Agendamento

async def seed_historico_python():
    print("🚀 Iniciando povoamento do histórico de ligações via Python...")
    
    async with AsyncSessionLocal() as db:
        # 1. Buscar todos os idosos ativos
        result = await db.execute(select(Idoso).filter(Idoso.ativo == True))
        idosos = result.scalars().all()
        
        if not idosos:
            print("⚠️ Nenhum idoso encontrado para popular.")
            return

        print(f"📍 Encontrados {len(idosos)} idosos. Gerando {len(idosos) * 5} registros de histórico...")

        sentimentos = ["feliz", "neutro", "triste", "ansioso", "confuso"]
        qualidades = ["excelente", "boa", "regular", "ruim"]
        resumos = [
            "Idoso confirmou ingestão de medicamentos e relatou estar bem.",
            "Ligação de rotina para check-in de bem-estar. Paciente calmo.",
            "Tentativa de contato sem sucesso. Deixado recado.",
            "Conversa sobre consulta médica agendada para amanhã.",
            "Idoso relatou leve tontura, família foi notificada preventivamente."
        ]

        # 2. Para cada idoso, criar 5 registros
        for idoso in idosos:
            print(f"  - Populando histórico para: {idoso.nome}")
            
            for i in range(5):
                # Gera dados aleatórios
                concluida = random.choice([True, True, True, False]) # 75% de chance de sucesso
                objetivo = concluida and random.choice([True, True, False])
                duracao = random.randint(30, 300) if concluida else 0
                
                inicio = datetime.now() - timedelta(
                    days=random.randint(0, 10),
                    hours=random.randint(0, 23)
                )
                fim = inicio + timedelta(seconds=duracao)

                novo_historico = HistoricoLigacao(
                    idoso_id=idoso.id,
                    agendamento_id=None, # Opcional no modelo
                    twilio_call_sid=f"CA{random.getrandbits(64)}",
                    inicio_chamada=inicio,
                    fim_chamada=fim if concluida else None,
                    duracao_segundos=duracao,
                    modelo_utilizado="gemini-2.0-flash",
                    voice_name="Aoede",
                    qualidade_audio=random.choice(qualidades),
                    tarefa_concluida=concluida,
                    objetivo_alcancado=objetivo,
                    motivo_falha=None if concluida else "O idoso não atendeu a chamada.",
                    transcricao_resumo=random.choice(resumos) if concluida else "Chamada não atendida.",
                    sentimento_geral=random.choice(sentimentos) if concluida else None,
                    sentimento_intensidade=random.randint(1, 10) if concluida else None,
                    tokens_gemini=random.randint(500, 2000) if concluida else 0,
                    minutos_twilio=max(1, duracao // 60) if concluida else 0
                )
                db.add(novo_historico)
        
        # 3. Commit de todas as inserções
        await db.commit()
        print(f"✅ Sucesso! Foram criados {len(idosos) * 5} registros no histórico de ligações.")

if __name__ == "__main__":
    asyncio.run(seed_historico_python())
