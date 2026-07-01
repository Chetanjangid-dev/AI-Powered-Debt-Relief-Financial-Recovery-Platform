"""
auth.py
-------
Secure Session Management for AI Powered Debt Relief Platform.
Handles:
  1. Password hashing and verification (bcrypt)
  2. JWT token generation and validation
  3. User authentication (login)
  4. Current user extraction from token

Depends on: database.py, models.py
Used by: backend developer's FastAPI routes, e.g.
         POST /auth/register
         POST /auth/login
         GET  /auth/me

Install required packages:
    pip install passlib[bcrypt] python-jose[cryptography]
"""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

import models

# ---------- CONFIGURATION ----------

SECRET_KEY = "change-this-to-a-long-random-secret-key-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # token valid for 1 hour

# ---------- PASSWORD HASHING ----------

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Converts plain text password to bcrypt hash."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Returns True if plain password matches stored hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ---------- JWT TOKEN ----------

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a signed JWT token containing user data.
    Token expires after ACCESS_TOKEN_EXPIRE_MINUTES by default.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodes and validates a JWT token.
    Returns payload dict if valid, None if expired or invalid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# ---------- AUTHENTICATION ----------

def authenticate_user(db: Session, email: str, password: str):
    """
    Verifies email + password against database.
    Returns user object if valid, None if invalid.
    Used in login endpoint.
    """
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def get_current_user(db: Session, token: str):
    """
    Extracts current logged-in user from JWT token.
    Returns user object or None if token is invalid/expired.
    Used as a dependency in protected FastAPI routes.

    Backend usage example:
        token = request.headers.get("Authorization").split(" ")[1]
        user = get_current_user(db, token)
        if not user:
            raise HTTPException(status_code=401, detail="Unauthorized")
    """
    payload = decode_access_token(token)
    if payload is None:
        return None
    email = payload.get("sub")
    if email is None:
        return None
    user = db.query(models.User).filter(models.User.email == email).first()
    return user


def register_user(db: Session, name: str, email: str, password: str):
    """
    Registers a new user:
    1. Checks if email already exists
    2. Hashes the password
    3. Saves user to database
    4. Returns new user object
    """
    existing = db.query(models.User).filter(models.User.email == email).first()
    if existing:
        raise ValueError("Email already registered")

    hashed = hash_password(password)
    new_user = models.User(name=name, email=email, password_hash=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user