from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Enum, ForeignKey, DateTime, func
from ..db import Base
import enum
from datetime import datetime

class Role(str, enum.Enum):
    BENEFICIARIO = "beneficiario"
    ASSISTENTE = "assistente"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str | None]
    social_name: Mapped[str | None]
    pronoun: Mapped[str | None] = mapped_column(String(50), nullable=True)
    profile_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    cpf: Mapped[str | None] = mapped_column(String(11), unique=True, nullable=True, index=True)
    password_hash: Mapped[str]
    role: Mapped[Role] = mapped_column(Enum(Role, values_callable=lambda x: [e.value for e in x]), default=Role.BENEFICIARIO)
    is_active: Mapped[bool] = mapped_column(default=True)

    # Relacionamento com assistente (beneficiário vinculado a um assistente)
    assistente_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    # Relacionamento com ONG
    org_id: Mapped[int | None] = mapped_column(ForeignKey("orgs.id"), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    chats = relationship("Chat", back_populates="user", foreign_keys="Chat.user_id")
    beneficiarios = relationship("User", remote_side=[id], backref="assistente")
    org = relationship("Org", back_populates="users")
