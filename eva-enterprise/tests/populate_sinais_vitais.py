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
from database.models import Idoso, SinaisVitais

# Load environment variables
load_dotenv()

fake = Faker('pt_BR')

def generate_vital_sign(tipo):
    if tipo == 'batimentos':
        val = random.randint(60, 100)
        return str(val), 'bpm'
    elif tipo == 'pressao':
        sistolica = random.randint(110, 140)
        diastolica = random.randint(70, 90)
        return f"{sistolica}/{diastolica}", 'mmHg'
    elif tipo == 'glicose':
        val = random.randint(70, 140)
        return str(val), 'mg/dL'
    elif tipo == 'peso':
        val = round(random.uniform(50.0, 90.0), 1)
        return str(val), 'kg'
    return "0", ""

async def populate_sinais_vitais():
    async with AsyncSessionLocal() as db:
        print(f"Iniciando geração de Sinais Vitais (ASYNC)...")
        
        try:
            # Busca IDs de idosos
            result = await db.execute(select(Idoso.id))
            idosos_ids = result.scalars().all()
            
            if not idosos_ids:
                print("Nenhum idoso encontrado.")
                return

            print(f"Encontrados {len(idosos_ids)} idosos. Gerando histórico de 1 semana...")
            
            count_created = 0
            now = datetime.now()
            
            for idoso_id in idosos_ids:
                for d in range(7):
                    current_date = now - timedelta(days=d)
                    
                    # 1. Batimentos (2x ao dia)
                    for hour in [8, 20]:
                        med_time = current_date.replace(hour=hour, minute=0, second=0)
                        val, unit = generate_vital_sign('batimentos')
                        sinal = SinaisVitais(
                            idoso_id=idoso_id,
                            tipo='batimentos',
                            valor=val,
                            unidade=unit,
                            data_medicao=med_time,
                            observacao="Medição de rotina"
                        )
                        db.add(sinal)
                        count_created += 1
                    
                    # 2. Pressão (1x ao dia)
                    med_time = current_date.replace(hour=9, minute=0, second=0)
                    val, unit = generate_vital_sign('pressao')
                    sinal = SinaisVitais(
                        idoso_id=idoso_id,
                        tipo='pressao',
                        valor=val,
                        unidade=unit,
                        data_medicao=med_time
                    )
                    db.add(sinal)
                    count_created += 1

            await db.commit()
            print(f"Sucesso! {count_created} registros de sinais vitais criados.")
            
        except Exception as e:
            print(f"Erro ao gerar sinais vitais: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(populate_sinais_vitais())
