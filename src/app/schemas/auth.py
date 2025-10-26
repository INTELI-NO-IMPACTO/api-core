from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime


# =============== Login/Register ===============

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    social_name: str | None = None
    cpf: str | None = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError('Senha deve ter no mínimo 6 caracteres')
        return v

    @field_validator('cpf')
    @classmethod
    def validate_cpf(cls, v: str | None) -> str | None:
        if v is None:
            return v
        cpf = ''.join(filter(str.isdigit, v))
        if len(cpf) != 11:
            raise ValueError('CPF deve ter 11 dígitos')
        return cpf


# =============== Token Responses ===============

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # segundos


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# =============== Anonymous Session ===============

class AnonymousSessionRequest(BaseModel):
    """Request para criar sessão anônima de chat"""
    pass


class AnonymousSessionResponse(BaseModel):
    session_id: str
    chat_id: int
    expires_in: int  # segundos


# =============== Current User ===============

class CurrentUserResponse(BaseModel):
    id: int
    email: str
    name: str | None
    social_name: str | None
    pronoun: str | None
    profile_image_url: str | None
    role: str
    is_active: bool
    org_id: int | None
    assistente_id: int | None

    class Config:
        from_attributes = True


# =============== Password Management ===============

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError('Nova senha deve ter no mínimo 6 caracteres')
        return v


class ResetPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordConfirm(BaseModel):
    token: str
    new_password: str

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError('Nova senha deve ter no mínimo 6 caracteres')
        return v
