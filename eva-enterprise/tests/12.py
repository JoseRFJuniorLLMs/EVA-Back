import os
import asyncio
import sys
from datetime import datetime, timedelta
from sqlalchemy import select
from dotenv import load_dotenv

# Importa conexão e modelos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.connection import AsyncSessionLocal
from database.models import Agendamento

# Load environment variables
load_dotenv()

async def agendar_teste_curto_prazo():
    async with AsyncSessionLocal() as db:
        print(f"Iniciando agendamento de teste (5min/1h) para Idoso 120...")
        
        idoso_id = 120
        
        # Configuração do tempo
        agora = datetime.now()
        inicio = agora + timedelta(minutes=2) # Começa daqui a 2 minutos (como no seu exemplo)
        fim = inicio + timedelta(hours=1)     # Duração de 1 hora
        intervalo_minutos = 5
        
        agendamentos_batch = []
        tempo_atual = inicio
        count = 0
        
        try:
            while tempo_atual < fim:
                agendamento = Agendamento(
                    idoso_id=idoso_id,
                    tipo='lembrete_medicamento',
                    data_hora_agendada=tempo_atual,
                    prioridade='alta',
                    status='agendado',
                    criado_em=datetime.now(),
                    dados_tarefa={
                        "mensagem": f"Teste Frequente {intervalo_minutos}min - {tempo_atual.strftime('%H:%M')}", 
                        "medicamento": "Teste Rápido"
                    }
                )
                
                agendamentos_batch.append(agendamento)
                count += 1
                
                # Avança 5 minutos
                tempo_atual += timedelta(minutes=intervalo_minutos)
            
            if agendamentos_batch:
                db.add_all(agendamentos_batch)
                await db.commit()
                print(f"Sucesso! {count} agendamentos criados para o Idoso {idoso_id}.")
                print(f"Primeiro agendamento: {inicio}")
                print(f"Último agendamento: {tempo_atual - timedelta(minutes=intervalo_minutos)}")
                
        except Exception as e:
            print(f"Erro ao gerar agendamentos: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(agendar_teste_curto_prazo())