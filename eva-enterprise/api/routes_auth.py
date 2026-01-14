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
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "viewer" # Default minimal role

class GoogleLoginRequest(BaseModel):
    token: str

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    # 1. Fetch User
    result = await db.execute(
        text("SELECT id, email, senha_hash as password_hash, tipo as role, ativo as active FROM usuarios WHERE email = :email"),
        {"email": form_data.email}
    )
    user = result.mappings().first()

    # 2. Validate
    if not user or not user["password_hash"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Verify hash OR plaintext (fallback for legacy/migrated users)
    if not verify_password(form_data.password, user["password_hash"]):
        # Fallback: Check if stored password is plain text
        if user["password_hash"] != form_data.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # TODO: Ideally re-hash here if plaintext matched

    if not user["active"]:
        raise HTTPException(status_code=400, detail="Inactive user")

    # 3. Create Token
    access_token_expires = timedelta(minutes=60 * 24) # 1 day
    access_token = create_access_token(
        data={"sub": user["email"], "role": user["role"], "user_id": user["id"]},
        expires_delta=access_token_expires
    )
    
    # 4. Audit Log (Async fire & forget usually, but here await)
    await db.execute(
        text("INSERT INTO auth_audit_logs (user_id, action, ip_address) VALUES (:uid, 'LOGIN', :ip)"),
        {"uid": user["id"], "ip": "0.0.0.0"} # TODO: catch request IP
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
    pwd_hash = get_password_hash(req.password)

    # 3. Insert
    # Only allow safe roles for public registration
    safe_role = "viewer" 
    if req.role in ["attendant", "viewer", "family"]:
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
        data={"sub": new_user["email"], "role": new_user["role"], "user_id": new_user["id"]}
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
            data={"sub": email, "role": user_role, "user_id": user_id}
        )
        return {"access_token": access_token, "token_type": "bearer"}

    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google Token")

@router.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user
