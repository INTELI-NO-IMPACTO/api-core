from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, ForeignKey, func
from ..db import Base
from datetime import datetime

class RefreshToken(Base):
    """Tokens de refresh para autenticação JWT"""
    __tablename__ = "refresh_tokens"
    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    token: Mapped[str] = mapped_column(String(500), unique=True, index=True)

    # Validade
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Controle de revogação
    is_revoked: Mapped[bool] = mapped_column(default=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
