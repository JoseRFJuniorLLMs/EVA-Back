import os
import random
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
        print(f"Iniciando geração de Agendamentos (ASYNC)...")
        
        try:
            # Busca IDs de idosos existentes
            result = await db.execute(select(Idoso.id))
            idosos = result.scalars().all()
            
            if not idosos:
                print("Nenhum idoso encontrado. Rode o script populate_db.py primeiro.")
                return

            print(f"Encontrados {len(idosos)} idosos. Gerando agendamentos...")
            
            count = 0
            for idoso_id in idosos:
                # Random date in the next 7 days
                days_ahead = random.randint(0, 7)
                hour = random.randint(8, 20)
                minutes = random.choice([0, 15, 30, 45])
                
                proximo_horario = datetime.now() + timedelta(days=days_ahead)
                proximo_horario = proximo_horario.replace(hour=hour, minute=minutes, second=0, microsecond=0)
                
                agendamento = Agendamento(
                    idoso_id=idoso_id,
                    tipo='medicamento',
                    data_hora_agendada=proximo_horario,
                    status='agendado',
                    dados_tarefa={"medicamento": fake.word().capitalize() + " 50mg", "dosagem": "1 comprimido"}
                )
                
                db.add(agendamento)
                count += 1

            await db.commit()
            print(f"Sucesso! {count} agendamentos criados.")
            
        except Exception as e:
            print(f"Erro ao gerar agendamentos: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(populate_agendamentos())
