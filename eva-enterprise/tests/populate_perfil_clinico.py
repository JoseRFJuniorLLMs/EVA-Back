import os
import random
import asyncio
import sys
from datetime import datetime
from sqlalchemy import select, Column, Integer, String, Text, ForeignKey, TIMESTAMP
from faker import Faker
from dotenv import load_dotenv

# Importa conexão e modelos centrais
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.connection import AsyncSessionLocal, Base
from database.models import Idoso

# Define o modelo localmente caso não esteja no models.py central
class IdosoPerfilClinico(Base):
    __tablename__ = 'idosos_perfil_clinico'
    idoso_id = Column(Integer, ForeignKey('idosos.id'), primary_key=True)
    tipo_sanguineo = Column(String(5))
    alergias = Column(Text)
    restricoes_locomocao = Column(Text)
    doencas_cronicas = Column(Text)
    atualizado_em = Column(TIMESTAMP, default=datetime.now)

# Load environment variables
load_dotenv()

fake = Faker('pt_BR')

async def populate_perfil_clinico():
    async with AsyncSessionLocal() as db:
        print(f"Iniciando geração de Perfil Clínico (ASYNC)...")
        
        try:
            # Busca IDs de idosos
            result = await db.execute(select(Idoso.id))
            idosos_ids = result.scalars().all()
            
            if not idosos_ids:
                print("Nenhum idoso encontrado.")
                return

            print(f"Encontrados {len(idosos_ids)} idosos. Verificando perfis existentes...")
            
            count_created = 0
            for idoso_id in idosos_ids:
                # Verifica se perfil já existe
                check_result = await db.execute(select(IdosoPerfilClinico).filter_by(idoso_id=idoso_id))
                if check_result.scalar_one_or_none():
                    continue

                alergias_list = fake.words(nb=3, ext_word_list=['Penicilina', 'Dipirona', 'Poeira', 'Amendoim', 'Nenhuma', 'Sulfa', 'Lactose'])
                
                perfil = IdosoPerfilClinico(
                    idoso_id=idoso_id,
                    tipo_sanguineo=random.choice(['A+', 'A-', 'B+', 'O+', 'O-', 'AB+']),
                    alergias=", ".join(alergias_list),
                    restricoes_locomocao=fake.sentence() if random.choice([True, False]) else None,
                    doencas_cronicas=fake.sentence()
                )
                
                db.add(perfil)
                count_created += 1

            await db.commit()
            print(f"Sucesso! {count_created} perfis clínicos criados.")
            
        except Exception as e:
            print(f"Erro ao gerar perfis clínicos: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(populate_perfil_clinico())
