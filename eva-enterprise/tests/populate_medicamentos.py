import os
import random
import asyncio
import sys
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm.attributes import flag_modified
from faker import Faker
from dotenv import load_dotenv

# Importa conexão e modelos centrais
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.connection import AsyncSessionLocal
from database.models import Idoso, Medicamento

# Load environment variables
load_dotenv()

fake = Faker('pt_BR')

async def populate_medicamentos(total_goal=50):
    async with AsyncSessionLocal() as db:
        print(f"Iniciando geração de {total_goal} Medicamentos (ASYNC)...")
        
        try:
            # Busca todos os idosos
            result = await db.execute(select(Idoso))
            idosos = result.scalars().all()
            
            if not idosos:
                print("Nenhum idoso encontrado.")
                return

            print(f"Encontrados {len(idosos)} idosos. Gerando medicamentos...")
            
            created_count = 0
            for _ in range(total_goal):
                idoso = random.choice(idosos)
                med_nome = fake.word().capitalize() + " " + str(random.choice([10, 20, 50, 100])) + "mg"
                
                med = Medicamento(
                    idoso_id=idoso.id,
                    nome=med_nome,
                    principio_ativo=fake.word(),
                    dosagem=str(random.choice([1, 2])) + " comprimido(s)",
                    horarios=[f"{random.randint(6,22):02d}:00"],
                    ativo=True
                )
                
                db.add(med)
                
                # Atualiza campo JSON de resumo no Idoso
                current_meds = list(idoso.medicamentos_atuais) if idoso.medicamentos_atuais else []
                current_meds.append(med_nome)
                idoso.medicamentos_atuais = current_meds
                flag_modified(idoso, "medicamentos_atuais")
                
                created_count += 1
                if created_count % 10 == 0:
                    print(f"Gerados {created_count}...")

            await db.commit()
            print(f"Sucesso! {created_count} medicamentos criados.")
            
        except Exception as e:
            print(f"Erro ao gerar medicamentos: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(populate_medicamentos(30))
