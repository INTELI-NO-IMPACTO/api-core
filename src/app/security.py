from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from .config import settings
import secrets

# Use bcrypt with explicit truncate_error=False to avoid compatibility issues
pwd_ctx = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__default_rounds=12,
    bcrypt__ident="2b",
)

# =============== Password Hashing ===============

def hash_password(password: str) -> str:
    """Hash de senha usando bcrypt"""
    return pwd_ctx.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica senha contra hash"""
    return pwd_ctx.verify(plain_password, hashed_password)


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
