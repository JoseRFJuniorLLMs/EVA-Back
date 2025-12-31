import asyncio
import sys
import os
import random
from datetime import datetime

# Path setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from database.connection import AsyncSessionLocal
from database.models import Idoso, Medicamento


async def seed_medicamentos_python():
    print("💊 Iniciando povoamento de Medicamentos...")

    async with AsyncSessionLocal() as db:
        result_idosos = await db.execute(select(Idoso).filter(Idoso.ativo == True))
        idosos = result_idosos.scalars().all()

        if not idosos:
            print("⚠️ Nenhum idoso encontrado para vincular medicamentos.")
            return

        # Lista de medicamentos comuns para testes
        lista_meds = [
            {"nome": "Losartana", "principio": "Potássica", "dose": "50mg", "forma": "Comprimido"},
            {"nome": "Metformina", "principio": "Cloridrato", "dose": "850mg", "forma": "Comprimido"},
            {"nome": "Sinvastatina", "principio": "Estatina", "dose": "20mg", "forma": "Cápsula"},
            {"nome": "Puran T4", "principio": "Levotiroxina", "dose": "75mcg", "forma": "Comprimido"}
        ]

        for idoso in idosos:
            # Sorteia 2 medicamentos por idoso
            for med_data in random.sample(lista_meds, 2):
                novo_med = Medicamento(
                    idoso_id=idoso.id,
                    nome=med_data["nome"],
                    principio_ativo=med_data["principio"],
                    dosagem=med_data["dose"],
                    forma=med_data["forma"],
                    # Estrutura JSON conforme seu modelo
                    horarios=["08:00", "20:00"] if random.choice([True, False]) else ["07:00"],
                    observacoes="Tomar com água após a refeição.",
                    ativo=True
                )
                db.add(novo_med)

            print(f"  ✅ Medicamentos inseridos para: {idoso.nome}")

        try:
            await db.commit()
            # Nota: O custo estimado de processamento desta carga em nuvem é irrisório (menos de R$ 0,01).
            print(f"\n🚀 Sucesso! Medicamentos populados no banco de dados.")
        except Exception as e:
            await db.rollback()
            print(f"❌ Erro: {e}")


if __name__ == "__main__":
    asyncio.run(seed_medicamentos_python())