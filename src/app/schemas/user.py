from pydantic import BaseModel, EmailStr, field_validator, model_validator
from typing import Optional
from datetime import datetime
from ..models.user import Role


# =============== Base Schemas ===============

class UserBase(BaseModel):
    email: EmailStr
    name: str | None = None
    social_name: str | None = None
    pronoun: str | None = None


class UserCreate(UserBase):
    password: str
    role: Role = Role.BENEFICIARIO
    cpf: str | None = None
    assistente_id: int | None = None
    org_id: int | None = None

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
        # Remove formatação
        cpf = ''.join(filter(str.isdigit, v))
        if len(cpf) != 11:
            raise ValueError('CPF deve ter 11 dígitos')
        return cpf


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    name: str | None = None
    social_name: str | None = None
    pronoun: str | None = None
    cpf: str | None = None
    is_active: bool | None = None
    assistente_id: int | None = None
    org_id: int | None = None

    @field_validator('cpf')
    @classmethod
    def validate_cpf(cls, v: str | None) -> str | None:
        if v is None:
            return v
        cpf = ''.join(filter(str.isdigit, v))
        if len(cpf) != 11:
            raise ValueError('CPF deve ter 11 dígitos')
        return cpf


class UserResponse(UserBase):
    id: int
    role: Role
    cpf: str | None
    profile_image_url: str | None
    is_active: bool
    assistente_id: int | None
    org_id: int | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============== Role-Specific Schemas ===============

class BeneficiarioCreate(UserBase):
    """Schema para criar beneficiário - assistente_id é obrigatório"""
    password: str
    cpf: str | None = None
    assistente_id: int  # Obrigatório para beneficiário
    org_id: int | None = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError('Senha deve ter no mínimo 6 caracteres')
        return v


class BeneficiarioUpdate(BaseModel):
    email: EmailStr | None = None
    name: str | None = None
    social_name: str | None = None
    pronoun: str | None = None
    cpf: str | None = None
    is_active: bool | None = None
    assistente_id: int | None = None
    org_id: int | None = None

    @field_validator('cpf')
    @classmethod
    def validate_cpf(cls, v: str | None) -> str | None:
        if v is None:
            return v
        cpf = ''.join(filter(str.isdigit, v))
        if len(cpf) != 11:
            raise ValueError('CPF deve ter 11 dígitos')
        return cpf


class AssistenteCreate(UserBase):
    """Schema para criar assistente - org_id é obrigatório"""
    password: str
    cpf: str | None = None
    org_id: int  # Obrigatório para assistente

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError('Senha deve ter no mínimo 6 caracteres')
        return v


class AdminCreate(UserBase):
    """Schema para criar admin - sem vínculos obrigatórios"""
    password: str
    cpf: str | None = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError('Senha deve ter no mínimo 6 caracteres')
        return v


# =============== List/Filter Schemas ===============

class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int
    page: int
    page_size: int


class VincularBeneficiarioRequest(BaseModel):
    """Request para vincular beneficiário a assistente"""
    beneficiario_id: int
    assistente_id: int
