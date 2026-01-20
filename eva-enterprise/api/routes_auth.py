from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from database.connection import get_db
from utils.security import verify_password, get_password_hash, create_access_token, get_current_user
from pydantic import BaseModel, EmailStr
from datetime import timedelta
import os
from google.oauth2 import id_token
from google.auth.transport import requests

router = APIRouter()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    email: EmailStr
    senha_hash: str

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    senha_hash: str
    role: str = "cuidador"  # Default role that matches DB constraint

class GoogleLoginRequest(BaseModel):
    token: str

from fastapi.security import OAuth2PasswordRequestForm

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    # 1. Fetch User with Subscription Tier
    result = await db.execute(
        text("SELECT id, email, senha_hash as password_hash, tipo as role, ativo as active FROM usuarios WHERE email = :email"),
        {"email": form_data.username}
    )
    user = result.mappings().first()

    # 2. Validate
    if not user or not user["password_hash"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    s_hash = user["password_hash"].strip()
    
    # Verify password hash
    if not verify_password(form_data.password, s_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user["active"]:
        raise HTTPException(status_code=400, detail="Inactive user")

    # 3. Create Token
    access_token_expires = timedelta(minutes=60 * 24) # 1 day
    access_token = create_access_token(
        data={
            "sub": user["email"], 
            "role": user["role"], 
            "user_id": user["id"],
            "subscription_tier": "basic"
        },
        expires_delta=access_token_expires
    )
    
    # 4. Audit Log (Async fire & forget usually, but here await)
    await db.execute(
        text("INSERT INTO audit_logs (usuario_email, acao, ip_address) VALUES (:email, 'LOGIN', :ip)"),
        {"email": user["email"], "ip": "0.0.0.0"} # TODO: catch request IP
    )
    await db.commit()

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=Token, status_code=201)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # 1. Check existing
    result = await db.execute(
        text("SELECT id FROM usuarios WHERE email = :email"),
        {"email": req.email}
    )
    if result.first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # 2. Hash Password
    pwd_hash = get_password_hash(req.senha_hash)

    # 3. Insert
    # Only allow safe roles for public registration
    safe_role = "cuidador"  # Default safe role
    if req.role in ["cuidador", "profissional"]:  # Don't allow admin via public registration
        safe_role = req.role

    query = text("""
        INSERT INTO usuarios (nome, email, senha_hash, tipo) 
        VALUES (:name, :email, :ph, :role) 
        RETURNING id, email, tipo as role
    """)
    result = await db.execute(query, {
        "name": req.name,
        "email": req.email,
        "ph": pwd_hash,
        "role": safe_role
    })
    new_user = result.mappings().first()
    await db.commit()

    # 4. Generate Token
    access_token = create_access_token(
        data={
            "sub": new_user["email"], 
            "role": new_user["role"], 
            "user_id": new_user["id"],
            "subscription_tier": "basic"  # Default for new users
        }
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/google", response_model=Token)
async def google_login(req: GoogleLoginRequest, db: AsyncSession = Depends(get_db)):
    try:
        # 1. Verify Google Token
        idinfo = id_token.verify_oauth2_token(req.token, requests.Request(), GOOGLE_CLIENT_ID)
        
        email = idinfo["email"]
        google_id = idinfo["sub"]
        name = idinfo.get("name", "")
        picture = idinfo.get("picture", "")

        # 2. Check DB
        result = await db.execute(
            text("SELECT id, email, tipo as role, ativo as active FROM usuarios WHERE email = :email"),
            {"email": email}
        )
        user = result.mappings().first()

        user_role = "viewer"
        user_id = None

        if not user:
            # Register new user from Google
            query = text("""
                INSERT INTO usuarios (nome, email, google_id, foto_url, tipo)
                VALUES (:name, :email, :gid, :url, 'viewer')
                RETURNING id, tipo as role
            """)
            res = await db.execute(query, {
                "name": name,
                "email": email,
                "gid": google_id,
                "url": picture
            })
            new_user = res.mappings().first()
            user_id = new_user["id"]
            user_role = new_user["role"]
            await db.commit()
        else:
            if not user["active"]:
                 raise HTTPException(status_code=400, detail="Inactive user")
            user_id = user["id"]
            user_role = user["role"]
            
            # Update google_id if missing
            await db.execute(
                text("UPDATE usuarios SET google_id = :gid, foto_url = :url WHERE id = :uid"),
                {"gid": google_id, "url": picture, "uid": user_id}
            )
            await db.commit()

        # 3. Create Token
        access_token = create_access_token(
            data={
                "sub": email, 
                "role": user_role, 
                "user_id": user_id,
                "subscription_tier": "basic"
            }
        )
        return {"access_token": access_token, "token_type": "bearer"}

    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google Token")

@router.get("/me")
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna informações do usuário logado
    """
    
    user_id = current_user.get('user_id')
    
    query = text("""
        SELECT id, nome, email, telefone, tipo, cpf, data_nascimento, ativo
        FROM usuarios
        WHERE id = :user_id
    """)
    
    result = await db.execute(query, {"user_id": user_id})
    user = result.mappings().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    return dict(user)

@router.put("/profile")
async def update_profile(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Atualiza perfil do usuário logado
    """
    
    user_id = current_user.get('user_id')
    
    # Campos permitidos para atualização
    allowed_fields = ['nome', 'telefone', 'cpf', 'data_nascimento']
    update_fields = []
    params = {'user_id': user_id}
    
    for field in allowed_fields:
        if field in data:
            update_fields.append(f"{field} = :{field}")
            params[field] = data[field]
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
    
    query = text(f"""
        UPDATE usuarios
        SET {', '.join(update_fields)}, atualizado_em = NOW()
        WHERE id = :user_id
        RETURNING id, nome, email, telefone, tipo, cpf, data_nascimento
    """)
    
    result = await db.execute(query, params)
    await db.commit()
    
    updated_user = result.mappings().first()
    
    if not updated_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    return dict(updated_user)

@router.patch("/change-password")
async def change_password(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Altera senha do usuário logado
    """
    
    user_id = current_user.get('user_id')
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        raise HTTPException(status_code=400, detail="Senhas antiga e nova são obrigatórias")
    
    # Buscar senha atual
    query = text("""
        SELECT senha_hash
        FROM usuarios
        WHERE id = :user_id
    """)
    
    result = await db.execute(query, {"user_id": user_id})
    user = result.mappings().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Verificar senha antiga
    if not bcrypt.checkpw(old_password.encode('utf-8'), user['senha_hash'].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Senha atual incorreta")
    
    # Hash da nova senha
    new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Atualizar senha
    update_query = text("""
        UPDATE usuarios
        SET senha_hash = :new_hash, atualizado_em = NOW()
        WHERE id = :user_id
    """)
    
    await db.execute(update_query, {"user_id": user_id, "new_hash": new_hash})
    await db.commit()
    
    return {"message": "Senha alterada com sucesso"}
