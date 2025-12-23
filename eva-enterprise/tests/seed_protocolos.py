
import asyncio
import sys
import os
import random
from datetime import datetime

# Adiciona o diretório raiz ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from database.connection import AsyncSessionLocal
from database.models import Idoso, ProtocoloAlerta, ProtocoloEtapa

async def seed_protocolos_python():
    print("🚀 Iniciando povoamento de protocolos e etapas via Python...")
    
    async with AsyncSessionLocal() as db:
        # 1. Buscar todos os idosos ativos
        result = await db.execute(select(Idoso).filter(Idoso.ativo == True))
        idosos = result.scalars().all()
        
        if not idosos:
            print("⚠️ Nenhum idoso encontrado para popular.")
            return

        print(f"📍 Encontrados {len(idosos)} idosos. Gerando protocolos...")

        acoes = ['RETRY', 'NOTIFY_WA', 'NOTIFY_SMS']
        contatos = ['Filho(a)', 'Cônjuge', 'Neto(a)', 'Vizinho(a)', 'Cuidador(a)']

        # 2. Para cada idoso, criar 5 protocolos
        for idoso in idosos:
            print(f"  - Populando idoso: {idoso.nome}")
            
            for p_idx in range(1, 6):
                nome_protocolo = f"Protocolo de {random.choice(['Emergência', 'Medicamentos', 'Rotina', 'Final de Semana', 'Noite'])} #{p_idx}"
                
                protocolo = ProtocoloAlerta(
                    idoso_id=idoso.id,
                    nome=nome_protocolo,
                    ativo=True
                )
                db.add(protocolo)
                await db.flush() # Para pegar o ID do protocolo recém criado

                # 3. Adicionar 3 etapas para cada protocolo
                for e_idx in range(1, 4):
                    acao = random.choice(acoes)
                    etapa = ProtocoloEtapa(
                        protocolo_id=protocolo.id,
                        ordem=e_idx,
                        acao=acao,
                        delay_minutos=random.randint(5, 30),
                        tentativas=random.randint(1, 3) if acao == 'RETRY' else 0,
                        contato_alvo=random.choice(contatos) if acao != 'RETRY' else None
                    )
                    db.add(etapa)
        
        # 4. Commit de todas as inserções
        await db.commit()
        print(f"✅ Sucesso! Foram criados {len(idosos) * 5} protocolos com múltiplas etapas.")

if __name__ == "__main__":
    asyncio.run(seed_protocolos_python())
