import secrets
from datetime import datetime, timedelta

import bcrypt
from jose import JWTError, jwt

from .config import settings

# =============== Password Hashing ===============

def hash_password(password: str) -> str:
    """Hash de senha usando bcrypt"""
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        raise ValueError("Senha deve ter no máximo 72 bytes")
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica senha contra hash"""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except ValueError:
        return False


# =============== JWT Tokens ===============

def create_access_token(user_id: int, expires_delta: timedelta | None = None) -> str:
    """Cria access token JWT"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRES_MIN)

    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access"
    }
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def create_refresh_token(user_id: int) -> str:
    """Cria refresh token JWT (válido por 7 dias)"""
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh"
    }
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def decode_token(token: str) -> dict | None:
    """Decodifica e valida token JWT"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
        return payload
    except JWTError:
        return None


def generate_session_id() -> str:
    """Gera ID de sessão anônima"""
    return f"anon_{secrets.token_urlsafe(32)}"


def generate_invite_code() -> str:
    """Gera código de convite aleatório (8 caracteres)"""
    return secrets.token_urlsafe(6).upper()[:8]
