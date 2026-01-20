from datetime import datetime, timedelta
from typing import Optional
import os
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from database.connection import get_db
import logging

logger = logging.getLogger(__name__)

# Config
SECRET_KEY = os.getenv("SECRET_KEY", "eva_secret_key_change_me_in_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password using bcrypt.
    Handles both string and bytes input gracefully.
    """
    try:
        # Ensure inputs are bytes
        if isinstance(plain_password, str):
            password_bytes = plain_password.encode('utf-8')
        else:
            password_bytes = plain_password
            
        if isinstance(hashed_password, str):
            hash_bytes = hashed_password.encode('utf-8')
        else:
            hash_bytes = hashed_password
        
        # Verify the hash starts with bcrypt prefix
        if not hash_bytes.startswith(b'$2b$') and not hash_bytes.startswith(b'$2a$'):
            logger.error(f"Invalid hash format. Hash should start with $2b$ or $2a$")
            return False
        
        # bcrypt has a 72 byte limit on passwords
        if len(password_bytes) > 72:
            logger.warning("Password exceeds 72 bytes, truncating for bcrypt compatibility")
            password_bytes = password_bytes[:72]
        
        return bcrypt.checkpw(password_bytes, hash_bytes)
        
    except ValueError as e:
        logger.error(f"ValueError in password verification: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in password verification: {e}", exc_info=True)
        return False


def get_password_hash(password: str) -> str:
    """
    Hash password using bcrypt.
    Uses a cost factor of 12 (secure but not too slow).
    """
    try:
        if isinstance(password, str):
            password_bytes = password.encode('utf-8')
        else:
            password_bytes = password
        
        # Truncate to 72 bytes if needed (bcrypt limitation)
        if len(password_bytes) > 72:
            logger.warning("Password exceeds 72 bytes, truncating for bcrypt compatibility")
            password_bytes = password_bytes[:72]
        
        # Generate salt and hash
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password_bytes, salt)
        
        return hashed.decode('utf-8')
        
    except Exception as e:
        logger.error(f"Error hashing password: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing password"
        )


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_db)
):
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        
        if email is None:
            raise credentials_exception
            
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise credentials_exception
    
    try:
        # Query database for user
        result = await db.execute(
            text("""
                SELECT 
                    id, 
                    nome as name, 
                    email, 
                    tipo as role, 
                    ativo as active,
                    plano_assinatura as subscription_tier
                FROM usuarios 
                WHERE email = :email
            """), 
            {"email": email}
        )
        user = result.mappings().first()
        
        if user is None:
            logger.warning(f"User not found in database: {email}")
            raise credentials_exception
            
        if not user["active"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user account"
            )
        
        return dict(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error in get_current_user: {e}", exc_info=True)
        raise credentials_exception


def check_role(required_roles: list):
    """Dependency to check if user has required role"""
    async def role_checker(user = Depends(get_current_user)):
        user_role = user.get("role", "")
        
        # Admin always has access
        if user_role == "admin":
            return user
        
        # Check if user has any of the required roles
        if user_role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required roles: {', '.join(required_roles)}"
            )
        
        return user
    
    return role_checker


def require_subscription(min_tier: str = "basic"):
    """
    Dependency to require minimum subscription tier.
    Hierarchy: basic < gold < diamond
    """
    tiers = {"basic": 0, "gold": 1, "diamond": 2}
    
    async def subscription_checker(user = Depends(get_current_user)):
        # Admin always has access
        if user.get("role") == "admin":
            return user
        
        user_tier = user.get("subscription_tier", "basic")
        
        # Validate tier exists
        if user_tier not in tiers:
            logger.warning(f"Invalid subscription tier: {user_tier}")
            user_tier = "basic"
        
        # Check if user meets minimum tier
        if tiers.get(user_tier, 0) < tiers.get(min_tier, 0):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Subscription tier '{min_tier}' or higher required. Your tier: '{user_tier}'"
            )
        
        return user
    
    return subscription_checker
