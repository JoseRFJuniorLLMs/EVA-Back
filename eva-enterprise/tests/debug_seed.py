
import sys
import os
import asyncio
from sqlalchemy import select, text

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from database.connection import AsyncSessionLocal

async def test_conn():
    print("Iniciando teste de conexão...")
    try:
        async with AsyncSessionLocal() as session:
            print("Session criada.")
            # Teste 1: Query simples de texto
            print("Executando SELECT 1...")
            result = await session.execute(text("SELECT 1"))
            val = result.scalar()
            print("Resultado SELECT 1: {val}")

            # Teste 2: ORM Query
            from database.models import Idoso
            print("Executando SELECT(Idoso)...")
            stmt = select(Idoso).limit(1)
            result = await session.execute(stmt)
            idoso = result.scalars().first()
            print(f"Idoso encontrado: {idoso.nome if idoso else 'Nenhum'}")
    except Exception as e:
        print(f"ERRO TESTE 1: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_conn())
