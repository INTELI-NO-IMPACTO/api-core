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
    rating: int | None
    rating_comment: str | None
    rated_at: datetime | None
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


# =============== Rating System ===============

class ChatRatingCreate(BaseModel):
    """Schema para avaliar uma conversa"""
    rating: int
    comment: str | None = None

    @field_validator('rating')
    @classmethod
    def validate_rating(cls, v: int) -> int:
        if v < 0 or v > 5:
            raise ValueError('Rating deve estar entre 0 e 5')
        return v

    @field_validator('comment')
    @classmethod
    def validate_comment(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 1000:
            raise ValueError('Comentário muito longo (máx 1000 caracteres)')
        return v


class ChatRatingResponse(BaseModel):
    """Response após avaliar conversa"""
    chat_id: int
    rating: int
    rating_comment: str | None
    rated_at: datetime
    message: str


class ChatRatingStatsResponse(BaseModel):
    """Estatísticas gerais de avaliações"""
    total_ratings: int
    average_rating: float
    rating_distribution: dict[int, int]  # {0: count, 1: count, ...}
    total_chats: int
    percentage_rated: float
