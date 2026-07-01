import sys
import os
import models

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "Database"))

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt

from app.core.database import get_db
from app.utils.exceptions import DatabaseError

# Use sha256_crypt instead of bcrypt — avoids bcrypt 5.0 compatibility issue
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

SECRET_KEY = "debt-relief-platform-secret-key-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_token(email: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": email, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        return None


@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Registers a new user account.
    Frontend sends: name, email, password
    Returns: user info + JWT token
    """
    # Check email already exists
    existing = db.query(models.User).filter(
        models.User.email == request.email
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    new_user = models.User(
        name=request.name,
        email=request.email,
        password_hash=hash_password(request.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_token(new_user.email)
    return {
        "success": True,
        "message": "Account created successfully",
        "token": token,
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email
        }
    }


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Logs in an existing user.
    Frontend sends: email, password
    Returns: JWT token + user info
    """
    user = db.query(models.User).filter(
        models.User.email == request.email
    ).first()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_token(user.email)
    return {
        "success": True,
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }


@router.get("/me")
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Returns current logged in user from JWT token.
    Frontend sends: Bearer token in Authorization header
    Returns: user info
    """
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    email = payload.get("sub")
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return {
        "success": True,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }