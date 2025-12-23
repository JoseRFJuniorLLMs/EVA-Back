import os
import random
import asyncio
import sys
from datetime import datetime
from sqlalchemy import select
from faker import Faker
from dotenv import load_dotenv

# Importa conexão e modelos centrais
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.connection import AsyncSessionLocal
from database.models import Idoso, LegadoDigital

# Load environment variables
load_dotenv()

fake = Faker('pt_BR')

async def populate_memorias():
    async with AsyncSessionLocal() as db:
        print(f"Iniciando geração de Memórias (Legado Digital) (ASYNC)...")
        
        try:
            # Busca IDs de idosos
            result = await db.execute(select(Idoso.id))
            idosos_ids = result.scalars().all()
            
            if not idosos_ids:
                print("Nenhum idoso encontrado.")
                return

            print(f"Encontrados {len(idosos_ids)} idosos. Gerando memórias...")
            
            count_created = 0
            for idoso_id in idosos_ids:
                for _ in range(3):
                    tipo_memoria = random.choice(['audio', 'video', 'imagem', 'carta'])
                    
                    titulo = ""
                    if tipo_memoria == 'audio':
                        titulo = f"Áudio sobre {fake.word()}"
                    elif tipo_memoria == 'video':
                        titulo = f"Vídeo do {fake.word()}"
                    elif tipo_memoria == 'imagem':
                        titulo = f"Foto em {fake.city()}"
                    else:
                        titulo = f"Carta para {fake.first_name()}"

                    memoria = LegadoDigital(
                        idoso_id=idoso_id,
                        tipo_midia=tipo_memoria,
                        titulo=titulo,
                        url_arquivo=fake.url(),
                        descricao=fake.sentence()
                    )
                    db.add(memoria)
                    count_created += 1

            await db.commit()
            print(f"Sucesso! {count_created} memórias criadas.")
            
        except Exception as e:
            print(f"Erro ao gerar memórias: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(populate_memorias())
