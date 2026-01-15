from datetime import datetime, timedelta
from typing import Optional, Union
import os
from jose import JWTError, jwt
import bcrypt  # Using bcrypt directly instead of passlib
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from database.connection import get_db

# Config
SECRET_KEY = os.getenv("SECRET_KEY", "eva_secret_key_change_me_in_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 hours

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password using bcrypt directly"""
    try:
        # Convert strings to bytes
        password_bytes = plain_password.encode('utf-8')
        hash_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception as e:
        import logging
        logging.error(f"Password verification error: {e}")
        return False

def get_password_hash(password: str) -> str:
    """Hash password using bcrypt directly"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        if email is None:
            raise credentials_exception
        token_data = {"email": email, "role": role}
    except JWTError:
        raise credentials_exception
    
    # Check DB
    # Fix: Use 'usuarios' table (Portugues schema) matches routes_auth.py
    result = await db.execute(
        text("SELECT id, nome as name, email, tipo as role, ativo as active, subscription_tier FROM usuarios WHERE email = :email"), 
        {"email": email}
    )
    user = result.mappings().first()
    
    if user is None:
        raise credentials_exception
    if not user["active"]:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    return user

def check_role(required_roles: list):
    async def role_checker(user = Depends(get_current_user)):
        if user["role"] not in required_roles and "admin" not in user["role"]:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for this role"
            )
        return user
    return role_checker
