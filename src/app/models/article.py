from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum, String, Text, DateTime, func, ForeignKey, Integer
from ..db import Base
import enum
from datetime import datetime

class ArticleStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Article(Base):
    __tablename__ = "articles"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    body_md: Mapped[str] = mapped_column(Text)

    # Novos campos conforme requisito
    link_doc: Mapped[str | None] = mapped_column(String(500), nullable=True)
    link_image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    tags: Mapped[str] = mapped_column(String(500))  # "saude,documentos"

    status: Mapped[ArticleStatus] = mapped_column(default=ArticleStatus.PENDING)
    version: Mapped[int] = mapped_column(default=1)

    # Autor e aprovador
    author_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    approved_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

