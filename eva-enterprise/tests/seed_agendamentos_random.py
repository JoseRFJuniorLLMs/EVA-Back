import os
import random
import asyncio
import sys
from datetime import datetime, timedelta
from sqlalchemy import select
from faker import Faker
from dotenv import load_dotenv

# Path setup to import local modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.connection import AsyncSessionLocal
from database.models import Idoso, Agendamento

# Load environment variables
load_dotenv()

fake = Faker('pt_BR')

async def seed_agendamentos_random():
    async with AsyncSessionLocal() as db:
        print(f"Iniciando geração de 10 agendamentos por idoso...")
        
        try:
            # Busca todos os idosos
            result = await db.execute(select(Idoso))
            idosos = result.scalars().all()
            
            if not idosos:
                print("Nenhum idoso encontrado. Abortando.")
                return

            print(f"Encontrados {len(idosos)} idosos. Gerando {len(idosos) * 10} registros...")
            
            count = 0
            for idoso in idosos:
                for _ in range(10):
                    # Random date between 15 days ago and 15 days ahead
                    days_offset = random.randint(-15, 15)
                    hour = random.randint(8, 20)
                    minutes = random.choice([0, 15, 30, 45])
                    
                    data_agendada = datetime.now() + timedelta(days=days_offset)
                    data_agendada = data_agendada.replace(hour=hour, minute=minutes, second=0, microsecond=0)
                    
                    # Determine status based on date
                    if data_agendada < datetime.now():
                        status = random.choice(['concluido', 'falhou', 'cancelado'])
                    else:
                        status = 'agendado'

                    agendamento = Agendamento(
                        idoso_id=idoso.id,
                        tipo=random.choice(['medicamento', 'ligação_rotina', 'acompanhamento']),
                        data_hora_agendada=data_agendada,
                        status=status,
                        prioridade=random.choice(['baixa', 'normal', 'alta']),
                        dados_tarefa={
                            "instrucoes": fake.sentence(nb_words=10),
                            "notas": fake.text(max_nb_chars=50)
                        }
                    )
                    
                    db.add(agendamento)
                    count += 1

            await db.commit()
            print(f"Sucesso! {count} agendamentos criados com sucesso.")
            
        except Exception as e:
            print(f"Erro ao popular banco: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(seed_agendamentos_random())
