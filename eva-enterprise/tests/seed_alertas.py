import os
import random
import asyncio
import sys
from datetime import datetime, timedelta
from sqlalchemy import select

# Path setup to import local modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.connection import AsyncSessionLocal, DATABASE_URL, engine, Base
from database.models import Idoso, Alerta

async def seed_alertas():
    print(f"DEBUG: DATABASE_URL logada: {DATABASE_URL}")
    
    async with AsyncSessionLocal() as db:
        print("DEBUG: Criando tabelas se necessário...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
        print("DEBUG: Buscando idosos...")
        try:
            result = await db.execute(select(Idoso))
            idosos = result.scalars().all()
            
            if not idosos:
                print("ERRO: Nenhum idoso encontrado no banco!")
                return

            print(f"DEBUG: Encontrados {len(idosos)} idosos. Iniciando inserção...")
            
            count = 0
            # Valores estritamente alinhados com os CHECK constraints de eva-v7.sql
            tipos_validos = [
                'dose_esquecida',
                'efeito_colateral',
                'queda',
                'confusao_mental',
                'tristeza_profunda',
                'dor_intensa',
                'nao_atende_telefone',
                'alerta_ia',
                'outro'
            ]
            severidades_validas = ['baixa', 'aviso', 'alta', 'critica']
            
            for idoso in idosos:
                for i in range(10):
                    data_alerta = datetime.now() - timedelta(days=random.randint(0, 30))
                    tipo = random.choice(tipos_validos)
                    severidade = random.choice(severidades_validas)
                    
                    alerta = Alerta(
                        idoso_id=idoso.id,
                        tipo=tipo,
                        severidade=severidade,
                        mensagem=f"Alerta de teste {i+1} para {idoso.nome}: {tipo.replace('_', ' ').capitalize()}",
                        contexto_adicional={"test_seed": True, "generated_at": str(datetime.now())},
                        destinatarios=["Familiar", "Admin"], 
                        enviado=True,
                        data_envio=data_alerta,
                        visualizado=random.choice([True, False]),
                        resolvido=random.choice([True, False]),
                        criado_em=data_alerta
                    )
                    
                    db.add(alerta)
                    count += 1
                
                # Commit incremental
                if count % 100 == 0:
                    await db.commit()
                    print(f"DEBUG: {count} registros processados...")

            await db.commit()
            print(f"SUCESSO TOTAL: {count} alertas inseridos com sucesso!")
            
        except Exception as e:
            print(f"ERRO CRÍTICO no seed: {type(e).__name__}: {str(e)}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(seed_alertas())
