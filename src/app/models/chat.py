from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, DateTime, ForeignKey, func, Boolean, Integer, Float
from ..db import Base
from datetime import datetime

class Chat(Base):
    __tablename__ = "chats"
    id: Mapped[int] = mapped_column(primary_key=True)

    # Usuário dono do chat (pode ser None para sessões anônimas)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)

    # Sessão anônima (para chat sem login)
    session_id: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True, index=True)

    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(default=True)

    # Sistema de avaliação (rating de 0 a 5)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)  # Nota de 0 a 5
    rating_comment: Mapped[str | None] = mapped_column(Text, nullable=True)  # Comentário opcional
    rated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="chats", foreign_keys=[user_id])
    messages = relationship("ChatMessage", back_populates="chat", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id: Mapped[int] = mapped_column(primary_key=True)

    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"), index=True)

    # Quem enviou: user ou assistant
    role: Mapped[str] = mapped_column(String(20))  # "user" ou "assistant"

    content: Mapped[str] = mapped_column(Text)

    # Metadados opcionais
    message_metadata: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    chat = relationship("Chat", back_populates="messages")
