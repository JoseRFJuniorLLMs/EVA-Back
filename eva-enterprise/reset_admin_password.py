"""
Script para resetar senha do usuário admin.
Execute: python reset_admin_password.py
"""

import bcrypt
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import os
from dotenv import load_dotenv

load_dotenv()


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    password_bytes = password.encode('utf-8')
    
    # Truncate to 72 bytes (bcrypt limit)
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    return hashed.decode('utf-8')


async def reset_admin_password():
    """Reset admin password in database"""
    
    # Configuração do banco
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL não encontrada no .env")
        return
    
    # Criar engine assíncrono
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    # Email e nova senha
    admin_email = "admin@eva.com"
    new_password = "admin123"  # MUDE ISSO DEPOIS!
    
    # Gerar hash
    password_hash = hash_password(new_password)
    
    print(f"\n{'='*60}")
    print(f"📧 Email: {admin_email}")
    print(f"🔑 Nova Senha: {new_password}")
    print(f"🔐 Hash Gerado: {password_hash[:50]}...")
    print(f"{'='*60}\n")
    
    try:
        async with async_session() as session:
            # Verificar se usuário existe
            result = await session.execute(
                text("SELECT id, email, nome FROM usuarios WHERE email = :email"),
                {"email": admin_email}
            )
            user = result.mappings().first()
            
            if not user:
                print(f"❌ Usuário {admin_email} não encontrado!")
                
                # Criar novo usuário admin
                print("\n🔨 Criando novo usuário admin...")
                await session.execute(
                    text("""
                        INSERT INTO usuarios (nome, email, senha_hash, tipo, ativo, plano_assinatura)
                        VALUES (:nome, :email, :senha, :tipo, :ativo, :plano)
                    """),
                    {
                        "nome": "Administrador",
                        "email": admin_email,
                        "senha": password_hash,
                        "tipo": "admin",
                        "ativo": True,
                        "plano": "diamond"
                    }
                )
                await session.commit()
                print("✅ Usuário admin criado com sucesso!")
                
            else:
                # Atualizar senha
                print(f"\n🔄 Atualizando senha para: {user['nome']} ({user['email']})")
                await session.execute(
                    text("UPDATE usuarios SET senha_hash = :senha WHERE email = :email"),
                    {"senha": password_hash, "email": admin_email}
                )
                await session.commit()
                print("✅ Senha atualizada com sucesso!")
            
            # Verificar atualização
            result = await session.execute(
                text("SELECT email, tipo, ativo FROM usuarios WHERE email = :email"),
                {"email": admin_email}
            )
            updated_user = result.mappings().first()
            
            print(f"\n📋 Status Final:")
            print(f"   Email: {updated_user['email']}")
            print(f"   Tipo: {updated_user['tipo']}")
            print(f"   Ativo: {updated_user['ativo']}")
            print(f"\n{'='*60}")
            print(f"🎉 Agora você pode fazer login com:")
            print(f"   Email: {admin_email}")
            print(f"   Senha: {new_password}")
            print(f"{'='*60}\n")
            
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await engine.dispose()


if __name__ == "__main__":
    print("\n🔧 Script de Reset de Senha - EVA Backend\n")
    asyncio.run(reset_admin_password())
