from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .db import get_db
from .security import decode_token
from .models.user import User, Role

security = HTTPBearer()


# =============== Auth Dependencies ===============

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Retorna o usuário autenticado"""
    token = credentials.credentials
    payload = decode_token(token)

    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Retorna usuário ativo"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )
    return current_user


# =============== Role-Based Access Control ===============

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Requer permissão de admin"""
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: apenas administradores"
        )
    return current_user


def require_assistente(current_user: User = Depends(get_current_user)) -> User:
    """Requer permissão de assistente ou admin"""
    if current_user.role not in [Role.ASSISTENTE, Role.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: apenas assistentes ou administradores"
        )
    return current_user


def require_assistente_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """Alias para require_assistente"""
    return require_assistente(current_user)


# =============== Optional Auth (for anonymous sessions) ===============

def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> User | None:
    """Retorna usuário se autenticado, None caso contrário (para sessões anônimas)"""
    if not credentials:
        return None

    token = credentials.credentials
    payload = decode_token(token)

    if not payload or payload.get("type") != "access":
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    user = db.query(User).filter(User.id == int(user_id), User.is_active == True).first()
    return user
