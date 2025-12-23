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
from database.models import Idoso, Alerta

# Load environment variables
load_dotenv()

fake = Faker('pt_BR')

async def seed_alertas():
    async with AsyncSessionLocal() as db:
        print("Iniciando geração de 10 alertas por idoso...")
        
        try:
            # Busca todos os idosos
            result = await db.execute(select(Idoso))
            idosos = result.scalars().all()
            
            if not idosos:
                print("Nenhum idoso encontrado. Abortando.")
                return

            print(f"Encontrados {len(idosos)} idosos. Gerando {len(idosos) * 10} registros...")
            
            count = 0
            tipos = ["medicamento", "saude", "seguranca", "bem_estar", "cognitivo"]
            severidades = ["baixa", "media", "alta", "critica"]
            
            for idoso in idosos:
                for _ in range(10):
                    # Random date in the last 30 days
                    days_ago = random.randint(0, 30)
                    hours_ago = random.randint(0, 23)
                    minutes_ago = random.randint(0, 59)
                    data_alerta = datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
                    
                    # Some alerts are resolved, some are viewed, some are new
                    resolvido = random.choice([True, False])
                    visualizado = resolvido or random.choice([True, False])
                    
                    alerta = Alerta(
                        idoso_id=idoso.id,
                        tipo=random.choice(tipos),
                        severidade=random.choice(severidades),
                        mensagem=fake.sentence(nb_words=8),
                        contexto_adicional={"ia_confidence": random.uniform(0.7, 0.99)},
                        destinatarios=["Familiar", "Cuidador Principal"],
                        enviado=True,
                        data_envio=data_alerta + timedelta(minutes=2),
                        visualizado=visualizado,
                        data_visualizacao=data_alerta + timedelta(hours=random.randint(1, 4)) if visualizado else None,
                        resolvido=resolvido,
                        data_resolucao=data_alerta + timedelta(hours=random.randint(5, 24)) if resolvido else None,
                        resolucao_nota=fake.sentence(nb_words=5) if resolvido else None,
                        criado_em=data_alerta
                    )
                    
                    db.add(alerta)
                    count += 1

            await db.commit()
            print(f"Sucesso! {count} alertas criados com sucesso.")
            
        except Exception as e:
            print(f"Erro ao popular banco: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(seed_alertas())
