
import asyncio
import sys
import os
import random
from datetime import datetime, timedelta

# Adiciona o diretório raiz ao path para importar os módulos
# Se o script está em /tests/, o root é um nível acima
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from database.connection import AsyncSessionLocal
from database.models import Idoso, Timeline

async def seed_timeline_python():
    print("🚀 Iniciando povoamento da timeline via Python...")
    
    async with AsyncSessionLocal() as db:
        # 1. Buscar todos os idosos ativos
        result = await db.execute(select(Idoso).filter(Idoso.ativo == True))
        idosos = result.scalars().all()
        
        if not idosos:
            print("⚠️ Nenhum idoso encontrado para popular.")
            return

        print(f"📍 Encontrados {len(idosos)} idosos. Gerando eventos...")

        eventos_modelo = [
            {
                "tipo": "ligacao", 
                "subtipo": "sucesso", 
                "titulo": "Ligação Matinal", 
                "descricao": "EVA conversou com o idoso pela manhã. Tudo transcorreu dentro da normalidade."
            },
            {
                "tipo": "medicamento", 
                "subtipo": "sucesso", 
                "titulo": "Medicação Confirmada", 
                "descricao": "O idoso confirmou que tomou o remédio de uso contínuo conforme orientado."
            },
            {
                "tipo": "alerta", 
                "subtipo": "normal", 
                "titulo": "Check-in de Bem-Estar", 
                "descricao": "A EVA realizou uma breve conversa para verificar se o idoso tinha se alimentado corretamente."
            }
        ]

        # 2. Para cada idoso, criar 3 eventos aleatórios
        for idoso in idosos:
            print(f"  - Populando idoso: {idoso.nome}")
            
            for modelo in eventos_modelo:
                # Gera uma data aleatória nos últimos 5 dias
                data_evento = datetime.now() - timedelta(
                    days=random.randint(0, 5),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                
                novo_evento = Timeline(
                    idoso_id=idoso.id,
                    tipo=modelo["tipo"],
                    subtipo=modelo["subtipo"],
                    titulo=modelo["titulo"],
                    descricao=modelo["descricao"],
                    data=data_evento
                )
                db.add(novo_evento)
        
        # 3. Commit de todas as inserções
        await db.commit()
        print(f"✅ Sucesso! Foram criados {len(idosos) * 3} novos eventos na timeline.")

if __name__ == "__main__":
    asyncio.run(seed_timeline_python())
