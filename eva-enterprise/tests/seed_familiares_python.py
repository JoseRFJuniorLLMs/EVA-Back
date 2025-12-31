import asyncio
import sys
import os
import random
from datetime import datetime

# Adiciona o diretório raiz ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from database.connection import AsyncSessionLocal
from database.models import Idoso, MembroFamilia


async def seed_familiares_python():
    print("🌳 Iniciando povoamento de Membros da Família...")

    async with AsyncSessionLocal() as db:
        # 1. Buscar todos os idosos ativos
        result = await db.execute(select(Idoso).filter(Idoso.ativo == True))
        idosos = result.scalars().all()

        if not idosos:
            print("⚠️ Nenhum idoso encontrado. Popule os idosos antes de rodar este script.")
            return

        # Listas de apoio para dados fictícios
        nomes_homens = ["Carlos Silva", "João Oliveira", "Ricardo Santos", "André Lima", "Marcos Costa"]
        nomes_mulheres = ["Ana Paula", "Mariana Souza", "Beatriz Ferreira", "Juliana Mendes", "Cláudia Rocha"]
        parentescos = ["Filho(a)", "Neto(a)", "Sobrinho(a)", "Cônjuge", "Irmão/Irmã"]

        print(f"📍 Processando {len(idosos)} idosos...")

        for idoso in idosos:
            # Criamos 2 familiares para cada idoso
            for i in range(2):
                is_resp = (i == 0)  # O primeiro da iteração será o responsável
                sexo_aleatorio = random.choice(['H', 'M'])
                nome = random.choice(nomes_homens if sexo_aleatorio == 'H' else nomes_mulheres)

                novo_familiar = MembroFamilia(
                    idoso_id=idoso.id,
                    nome=f"{nome} ({idoso.nome})",
                    parentesco=random.choice(parentescos),
                    telefone=f"119{random.randint(70000000, 99999999)}",
                    is_responsavel=is_resp,
                    foto_url=f"https://api.dicebear.com/7.x/avataaars/svg?seed={nome.replace(' ', '')}"
                )
                db.add(novo_familiar)

            print(f"  ✅ Familiares vinculados ao idoso: {idoso.nome}")

        try:
            # 3. Commit das inserções
            await db.commit()
            print(f"\n🚀 Sucesso! Familiares inseridos com sucesso.")
            print(f"Nota: O custo de armazenamento dessa operação no Cloud SQL é menor que R$ 0,01.")
        except Exception as e:
            await db.rollback()
            print(f"❌ Erro ao inserir familiares: {e}")


if __name__ == "__main__":
    asyncio.run(seed_familiares_python())