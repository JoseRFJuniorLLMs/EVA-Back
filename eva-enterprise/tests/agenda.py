import os
import asyncio
import sys
from datetime import datetime, timedelta
from sqlalchemy import select
from faker import Faker
from dotenv import load_dotenv

# Importa conexão e modelos centrais
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.connection import AsyncSessionLocal
from database.models import Idoso, Agendamento

# Load environment variables
load_dotenv()

fake = Faker('pt_BR')

async def populate_agendamentos():
    async with AsyncSessionLocal() as db:
        print(f"Iniciando geração de Agendamentos Recorrentes (ASYNC)...")
        
        try:
            # 1. Busca IDs de idosos APENAS entre 116 e 150
            stmt = select(Idoso.id).where(Idoso.id.between(116, 150))
            result = await db.execute(stmt)
            idosos = result.scalars().all()
            
            if not idosos:
                print("Nenhum idoso encontrado no intervalo 116 a 150. Verifique o banco de dados.")
                return

            print(f"Encontrados {len(idosos)} idosos (Range 116-150).")
            print("Gerando agendamentos a cada 2 horas para os próximos 30 dias...")
            
            # Configuração do tempo
            data_inicio = datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1) # Começa na próxima hora cheia
            dias_para_gerar = 30 # Mês todo
            data_fim = data_inicio + timedelta(days=dias_para_gerar)
            intervalo_horas = 2
            
            agendamentos_batch = []
            count = 0
            
            # Loop Temporal (Data atual até Data Fim)
            tempo_atual = data_inicio
            while tempo_atual < data_fim:
                
                # Loop pelos Idosos (116 a 150)
                for idoso_id in idosos:
                    
                    # Cria nome de remédio aleatório para variar o JSON
                    nome_medicamento = fake.word().capitalize()
                    
                    agendamento = Agendamento(
                        idoso_id=idoso_id,
                        tipo='lembrete_medicamento', # Conforme seu exemplo de INSERT
                        data_hora_agendada=tempo_atual,
                        prioridade='alta',
                        status='agendado',
                        criado_em=datetime.now(),
                        # Estrutura JSON conforme o seu INSERT
                        dados_tarefa={
                            "mensagem": f"Lembrete: Hora do medicamento {nome_medicamento}", 
                            "medicamento": f"{nome_medicamento} 50mg"
                        }
                    )
                    
                    agendamentos_batch.append(agendamento)
                    count += 1
                
                # Avança 2 horas no tempo
                tempo_atual += timedelta(hours=intervalo_horas)
                
                # OTIMIZAÇÃO: Commit a cada 5.000 registros para não estourar a memória
                if len(agendamentos_batch) >= 5000:
                    db.add_all(agendamentos_batch)
                    await db.commit()
                    print(f"processando... {count} agendamentos inseridos até {tempo_atual}...")
                    agendamentos_batch = [] # Limpa a lista

            # Commit final do restante
            if agendamentos_batch:
                db.add_all(agendamentos_batch)
                await db.commit()

            print(f"Sucesso! {count} agendamentos criados para {len(idosos)} idosos.")
            
        except Exception as e:
            print(f"Erro ao gerar agendamentos: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(populate_agendamentos())