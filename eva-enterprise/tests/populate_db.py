import os
import random
import asyncio
from datetime import datetime, date, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from faker import Faker
from dotenv import load_dotenv

# Importa conexão e modelos centrais
from database.connection import AsyncSessionLocal
from database.models import Idoso, SinaisVitais, Medicamento, MembroFamilia

# Load environment variables
load_dotenv()

fake = Faker('pt_BR')

def generate_cpf():
    return fake.cpf()

def generate_phone():
    return fake.cellphone_number()

async def populate_database(num_records=50):
    async with AsyncSessionLocal() as db:
        print(f"Iniciando geração de {num_records} registros (ASYNC)...")
        
        try:
            for _ in range(num_records):
                # 1. Idoso
                sexo = random.choice(['M', 'F'])
                nome = fake.name_male() if sexo == 'M' else fake.name_female()
                data_nascimento = fake.date_of_birth(minimum_age=65, maximum_age=95)
                
                idoso = Idoso(
                    nome=nome,
                    data_nascimento=data_nascimento,
                    telefone=generate_phone(),
                    cpf=generate_cpf(),
                    foto_url=fake.image_url(),
                    intro_audio_url=fake.url(),
                    nivel_cognitivo=random.choice(['normal', 'leve', 'moderado', 'severo']),
                    limitacoes_auditivas=fake.boolean(chance_of_getting_true=30),
                    usa_aparelho_auditivo=fake.boolean(chance_of_getting_true=20),
                    limitacoes_visuais=fake.boolean(chance_of_getting_true=25),
                    mobilidade=random.choice(['independente', 'auxiliado', 'cadeira_rodas', 'acamado']),
                    tom_voz=random.choice(['formal', 'amigavel', 'maternal', 'jovial']),
                    preferencia_horario_ligacao=random.choice(['manha', 'tarde', 'noite', 'qualquer']),
                    medicamentos_atuais=[],
                    condicoes_medicas=fake.sentence(),
                    notas_gerais=fake.text(),
                    sentimento=random.choice(['feliz', 'neutro', 'triste', 'ansioso']),
                )
                
                db.add(idoso)
                await db.flush() # Get ID
                
                # 2. Familiares (1 a 2)
                num_familiares = random.randint(1, 2)
                for i in range(num_familiares):
                    familiar = MembroFamilia(
                        idoso_id=idoso.id,
                        nome=fake.name(),
                        parentesco=random.choice(['Filho(a)', 'Neto(a)', 'Sobrinho(a)', 'Irmão(ã)']),
                        telefone=generate_phone(),
                        is_responsavel=(i == 0)
                    )
                    db.add(familiar)
                    
                    if i == 0:
                        idoso.familiar_principal = {
                            "nome": familiar.nome,
                            "telefone": familiar.telefone,
                            "parentesco": familiar.parentesco
                        }

                # 3. Medicamentos (1 a 3)
                num_meds = random.randint(1, 3)
                med_list_names = []
                for _ in range(num_meds):
                    med_nome = fake.word().capitalize() + " " + str(random.choice([10, 20, 50, 100])) + "mg"
                    med = Medicamento(
                        idoso_id=idoso.id,
                        nome=med_nome,
                        dosagem=str(random.choice([1, 2])) + " comprimido(s)",
                        horarios=[f"{random.randint(6,22):02d}:00"],
                    )
                    db.add(med)
                    med_list_names.append(med_nome)
                
                idoso.medicamentos_atuais = med_list_names

            await db.commit()
            print("Dados gerados com sucesso!")
            
        except Exception as e:
            print(f"Erro ao popular banco dados: {e}")
            await db.rollback()

if __name__ == "__main__":
    import sys
    # Ajusta path para rodar de fora ou de dentro da pasta tests
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    asyncio.run(populate_database(10))
