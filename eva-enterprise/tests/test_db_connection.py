import os
import asyncio
import sys
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Fix sys.path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from database.connection import DATABASE_URL

async def test_connection():
    print(f"🔍 Testando conexão com: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL}")
    
    # Criamos um engine local apenas para teste rápido
    engine = create_async_engine(
        DATABASE_URL, 
        echo=True, 
        connect_args={"timeout": 10}
    )
    
    try:
        print("⏳ Tentando 'SELECT 1'...")
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            val = result.scalar()
            print(f"✅ SUCESSO! Resultado do Banco: {val}")
    except Exception as e:
        print(f"❌ FALHA TOTAL na conexão:")
        print(f"Tipo do erro: {type(e).__name__}")
        print(f"Mensagem: {str(e)}")
        
        # Dicas úteis based no erro
        if "TimeoutError" in str(e) or "ETIMEDOUT" in str(e):
            print("\n💡 Dica: O servidor não respondeu. Verifique se o IP 34.89.62.186 está acessível (Firewall ou DB fora).")
        elif "password authentication failed" in str(e):
            print("\n💡 Dica: Usuário ou senha incorretos no DATABASE_URL.")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_connection())
