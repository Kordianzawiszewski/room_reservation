import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from db import get_db
from models import User

load_dotenv()

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')

if JWT_SECRET_KEY is None:
    raise RuntimeError("JWT_SECRET_KEY is not set")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_hash = PasswordHash.recommended()

bearer_scheme = HTTPBearer()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)

def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=ALGORITHM
    )

def decode_access_token(token: str):
    return jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=[ALGORITHM]
    )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)):
    try:
        token = credentials.credentials
        data = decode_access_token(token)
        user_id = data.get("sub")
        user_id = int(user_id)
    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    stmt = select(User).where(User.id == user_id)
    existing_user = db.scalars(stmt).one_or_none()

    if existing_user is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    if not existing_user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive")

    return existing_user

def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    return current_user
