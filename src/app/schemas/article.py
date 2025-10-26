from pydantic import BaseModel, field_validator
from datetime import datetime
from ..models.article import ArticleStatus


# =============== Base Schemas ===============

class ArticleBase(BaseModel):
    title: str
    body_md: str
    tags: str  # Comma-separated tags: "saude,documentos,cpf"
    link_doc: str | None = None
    link_image: str | None = None


class ArticleCreate(ArticleBase):
    """Schema para criar artigo"""
    status: ArticleStatus = ArticleStatus.DRAFT

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        if len(v) < 3:
            raise ValueError('Título deve ter no mínimo 3 caracteres')
        return v

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError('Pelo menos uma tag é obrigatória')
        return v.lower().strip()


class ArticleUpdate(BaseModel):
    """Schema para atualizar artigo (apenas campos que deseja modificar)"""
    title: str | None = None
    body_md: str | None = None
    tags: str | None = None
    link_doc: str | None = None
    link_image: str | None = None
    status: ArticleStatus | None = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        if v is not None and len(v.strip()) < 3:
            raise ValueError('Título deve ter no mínimo 3 caracteres')
        return v

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: str | None) -> str | None:
        if v is not None:
            cleaned = v.strip()
            if len(cleaned) == 0:
                raise ValueError('Tags não podem estar vazias')
            return cleaned.lower()
        return v


class ArticleResponse(ArticleBase):
    id: int
    slug: str
    status: ArticleStatus
    version: int
    author_id: int | None
    approved_by_id: int | None
    created_at: datetime
    updated_at: datetime
    approved_at: datetime | None

    class Config:
        from_attributes = True


# =============== Approval System ===============

class ApproveArticleRequest(BaseModel):
    """Request para aprovar artigo (admin only)"""
    article_id: int
    approved: bool  # True = aprovar, False = rejeitar
    reason: str | None = None


class ArticleApprovalResponse(BaseModel):
    article_id: int
    status: ArticleStatus
    approved_by_id: int
    approved_at: datetime
    message: str


# =============== List/Filter Schemas ===============

class ArticleListResponse(BaseModel):
    articles: list[ArticleResponse]
    total: int
    page: int
    page_size: int


class ArticleFilterParams(BaseModel):
    """Parâmetros de filtro para listagem de artigos"""
    status: ArticleStatus | None = None
    tags: str | None = None  # Filter by tag
    search: str | None = None  # Search in title and body
    author_id: int | None = None
    page: int = 1
    page_size: int = 20

    @field_validator('page')
    @classmethod
    def validate_page(cls, v: int) -> int:
        if v < 1:
            raise ValueError('Página deve ser maior que 0')
        return v

    @field_validator('page_size')
    @classmethod
    def validate_page_size(cls, v: int) -> int:
        if v < 1 or v > 100:
            raise ValueError('page_size deve estar entre 1 e 100')
        return v


# =============== Search ===============

class ArticleSearchRequest(BaseModel):
    query: str
    tags: list[str] | None = None
    limit: int = 10

    @field_validator('limit')
    @classmethod
    def validate_limit(cls, v: int) -> int:
        if v < 1 or v > 50:
            raise ValueError('limit deve estar entre 1 e 50')
        return v
