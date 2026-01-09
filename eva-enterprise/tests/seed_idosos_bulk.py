import os
import random
import asyncio
import sys
from datetime import datetime
from faker import Faker
from dotenv import load_dotenv

# Fix sys.path to include 'eva-enterprise' directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir) # eva-enterprise
sys.path.append(parent_dir)

try:
    from database.connection import AsyncSessionLocal, engine, Base
    from database.models import Idoso
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    sys.exit(1)

load_dotenv()

fake = Faker('pt_BR')

def gerar_cpf_limpo():
    """Gera CPF sem máscara (apenas números)"""
    return fake.cpf().replace('.', '').replace('-', '')

async def seed_idosos(n=1000):
    async with AsyncSessionLocal() as db:
        print(f"🚀 Iniciando seed de {n} idosos no banco de dados...")
        
        batch_size = 10000000
        total_batches = (n // batch_size) + (1 if n % batch_size > 0 else 0)
        
        for b in range(total_batches):
            current_batch_size = min(batch_size, n - (b * batch_size))
            idosos_batch = []
            
            for _ in range(current_batch_size):
                sexo = random.choice(['M', 'F'])
                nome = fake.name_male() if sexo == 'M' else fake.name_female()
                
                idoso = Idoso(
                    nome=nome,
                    data_nascimento=fake.date_of_birth(minimum_age=65, maximum_age=98),
                    telefone=fake.cellphone_number(),
                    cpf=gerar_cpf_limpo(),  # ← MUDANÇA AQUI
                    foto_url=f"https://i.pravatar.cc/150?u={fake.uuid4()}",
                    intro_audio_url=f"https://storage.googleapis.com/eva-assets/intros/{fake.uuid4()}.mp3",
                    
                    nivel_cognitivo=random.choice(['normal', 'leve', 'moderado', 'severo']),
                    limitacoes_auditivas=fake.boolean(chance_of_getting_true=25),
                    usa_aparelho_auditivo=fake.boolean(chance_of_getting_true=15),
                    limitacoes_visuais=fake.boolean(chance_of_getting_true=20),
                    mobilidade=random.choice(['independente', 'auxiliado', 'cadeira_rodas', 'acamado']),
                    
                    tom_voz=random.choice(['formal', 'amigavel', 'maternal', 'jovial']),
                    preferencia_horario_ligacao=random.choice(['manha', 'tarde', 'noite', 'qualquer']),
                    timezone="America/Sao_Paulo",
                    
                    ganho_audio_entrada=random.randint(-2, 2),
                    ganho_audio_saida=random.randint(-2, 2),
                    ambiente_ruidoso=fake.boolean(chance_of_getting_true=10),
                    
                    familiar_principal={
                        "nome": fake.name(),
                        "telefone": fake.cellphone_number(),
                        "parentesco": random.choice(['Filho(a)', 'Neto(a)', 'Cônjuge', 'Sobrinho(a)'])
                    },
                    contato_emergencia={
                        "nome": fake.name(),
                        "telefone": fake.cellphone_number(),
                        "parentesco": random.choice(['Filho(a)', 'Vizinho(a)', 'Médico', 'Amigo(a)'])
                    },
                    medico_responsavel={
                        "nome": f"Dr(a). {fake.last_name()}",
                        "telefone": fake.cellphone_number(),
                        "crm": f"{random.randint(100000, 999999)}/SP"
                    },
                    
                    medicamentos_atuais=[fake.word().capitalize() for _ in range(random.randint(1, 4))],
                    condicoes_medicas=random.choice([
                        "Hipertensão controlada",
                        "Diabetes Mellitus Tipo 2, Arritmia",
                        "Osteoporose, Colesterol alto",
                        "Histórico de AVC leve, reabilitação",
                        "Visão reduzida, sem doenças graves",
                        "Artrite reumatóide, dores nas juntas"
                    ]),
                    
                    sentimento=random.choice(['feliz', 'neutro', 'triste', 'ansioso', 'irritado', 'confuso', 'apatico']),
                    agendamentos_pendentes=0,
                    
                    notas_gerais=fake.text(max_nb_chars=150),
                    ativo=True
                )
                idosos_batch.append(idoso)
            
            try:
                db.add_all(idosos_batch)
                await db.commit()
                print(f"✅ Batch {b+1}/{total_batches} concluído ({len(idosos_batch)} registros)")
            except Exception as e:
                print(f"❌ Erro ao salvar batch {b+1}: {e}")
                await db.rollback()

        print("\n✨ Geração de 1000 idosos finalizada!")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed_idosos(1000))