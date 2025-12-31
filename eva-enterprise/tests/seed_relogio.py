import random
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy import create_engine, MetaData, insert, select

# URL DO SEU BANCO
DATABASE_URL = "postgresql+psycopg2://postgres:Debian23%40@34.39.249.108:5432/eva-db"

fake = Faker('pt_BR')
metadata = MetaData()


def run_seed():
    engine = create_engine(DATABASE_URL)
    print("🔍 Conectando e lendo a estrutura real do banco...")
    metadata.reflect(bind=engine)

    t_usuarios = metadata.tables.get('usuarios')
    tab_saude = ['atividade', 'sinais_vitais', 'sono', 'medicao_corporal', 'nutricao']

    # IDs solicitados
    ids_usuarios = [1] + list(range(116, 200))

    with engine.begin() as conn:
        print(f"👤 Passo 1: Criando {len(ids_usuarios)} usuários...")
        for uid in ids_usuarios:
            check = conn.execute(select(t_usuarios.c.id).where(t_usuarios.c.id == uid)).fetchone()
            if not check:
                conn.execute(insert(t_usuarios).values({
                    "id": uid,
                    "nome": fake.name(),
                    "email": fake.unique.email(),
                    "senha_hash": "fake_hash_123",
                    "tipo": "cuidador",
                    "ativo": True
                }))

        print("📊 Passo 2: Inserindo dados de saúde...")
        for uid in ids_usuarios:
            ts = datetime.now()

            for nome_tab in tab_saude:
                t = metadata.tables.get(nome_tab)
                if t is None: continue

                # DETECTA O NOME DA COLUNA DE ID (idoso_id ou cliente_id)
                col_id = 'idoso_id' if 'idoso_id' in t.columns else 'cliente_id'

                # Monta os dados base
                payload = {
                    col_id: uid,
                    "timestamp_coleta": ts,
                    "criado_em": ts
                }

                # Preenche campos específicos conforme a tabela
                if nome_tab == 'atividade':
                    payload.update({"passos": random.randint(1000, 10000), "distancia_km": random.uniform(1, 5),
                                    "tipo_exercicio": "caminhada"})
                elif nome_tab == 'sinais_vitais':
                    payload.update({"bpm": random.randint(60, 100), "pressao_sistolica": 120, "pressao_diastolica": 80,
                                    "spo2": 98})
                elif nome_tab == 'nutricao':
                    payload.update(
                        {"ingestao_agua_ml": 2000, "calorias_consumidas": 2000, "vitaminas_json": {"vit": "c"}})
                elif nome_tab == 'sono':
                    payload.update({"duracao_total_minutos": 480})
                elif nome_tab == 'medicao_corporal':
                    payload.update({"peso_kg": 75.0, "altura_cm": 170.0})

                # FILTRA APENAS O QUE EXISTE NA TABELA FÍSICA
                dados_validos = {k: v for k, v in payload.items() if k in t.columns}

                try:
                    conn.execute(insert(t).values(dados_validos))
                except Exception as e:
                    print(f"⚠️ Pulando registro na tabela {nome_tab}: {e}")

            if uid % 100 == 0:
                print(f"   ✅ Usuário {uid} e dependências OK.")

    print("\n🏆 FINALIZADO COM SUCESSO!")


if __name__ == "__main__":
    run_seed()