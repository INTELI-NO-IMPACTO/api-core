from pydantic import BaseModel, field_validator
from datetime import datetime


# =============== Chat Schemas ===============

class ChatCreate(BaseModel):
    """Schema para criar chat (autenticado ou anônimo)"""
    title: str | None = None
    session_id: str | None = None  # Para sessão anônima


class ChatUpdate(BaseModel):
    title: str | None = None
    summary: str | None = None
    is_active: bool | None = None


class ChatResponse(BaseModel):
    id: int
    user_id: int | None
    session_id: str | None
    title: str | None
    summary: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============== Chat Message Schemas ===============

class ChatMessageCreate(BaseModel):
    """Schema para criar mensagem no chat"""
    content: str
    role: str = "user"  # "user" ou "assistant"

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        if len(v.strip()) == 0:
            raise ValueError('Mensagem não pode ser vazia')
        if len(v) > 10000:
            raise ValueError('Mensagem muito longa (máx 10000 caracteres)')
        return v

    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in ['user', 'assistant']:
            raise ValueError('Role deve ser "user" ou "assistant"')
        return v


class ChatMessageResponse(BaseModel):
    id: int
    chat_id: int
    role: str
    content: str
    message_metadata: str | None
    created_at: datetime

    class Config:
        from_attributes = True


# =============== Chat with Messages ===============

class ChatWithMessagesResponse(ChatResponse):
    """Chat completo com histórico de mensagens"""
    messages: list[ChatMessageResponse]


# =============== List Schemas ===============

class ChatListResponse(BaseModel):
    chats: list[ChatResponse]
    total: int
    page: int
    page_size: int


# =============== Chat Summary ===============

class GenerateSummaryRequest(BaseModel):
    """Request para gerar resumo de um chat"""
    chat_id: int


class ChatSummaryResponse(BaseModel):
    chat_id: int
    summary: str
    message_count: int
    created_at: datetime
    updated_at: datetime
