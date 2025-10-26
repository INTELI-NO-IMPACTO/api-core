import re
from datetime import datetime
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from ..db import get_db
from ..dependencies import get_current_user
from ..models.article import Article, ArticleStatus
from ..models.user import User
from ..schemas.article import (
    ApproveArticleRequest,
    ArticleApprovalResponse,
    ArticleFilterParams,
    ArticleListResponse,
    ArticleResponse,
    ArticleUpdate,
)
from ..utils.supabase import get_supabase_storage_service

router = APIRouter(prefix="/articles", tags=["articles"])


def _generate_slug(title: str) -> str:
    slug = "-".join(part for part in title.lower().strip().split() if part)
    return "".join(ch for ch in slug if ch.isalnum() or ch == "-")


def _sanitize_filename(filename: str) -> str:
    """Sanitize filename to only allow alphanumeric, dots, hyphens, and underscores."""
    if not filename:
        return "file"

    # Get the file extension
    path = Path(filename)
    name = path.stem
    ext = path.suffix

    # Remove or replace invalid characters from the name
    # Allow only: letters, numbers, hyphens, underscores
    name = re.sub(r'[^\w\-]', '_', name)

    # Remove consecutive underscores and trim
    name = re.sub(r'_+', '_', name).strip('_')

    # If name is empty after sanitization, use a default
    if not name:
        name = "file"

    # Sanitize extension (remove any non-alphanumeric except dot)
    ext = re.sub(r'[^\w.]', '', ext)

    return f"{name}{ext}"


def _ensure_unique_slug(db: Session, slug: str, article_id: int | None = None) -> str:
    base_slug = slug or "article"
    candidate = base_slug
    suffix = 1
    while True:
        query = db.query(Article).filter(Article.slug == candidate)
        if article_id:
            query = query.filter(Article.id != article_id)
        exists = query.first()
        if not exists:
            return candidate
        suffix += 1
        candidate = f"{base_slug}-{suffix}"


@router.get("", response_model=ArticleListResponse)
def list_articles(
    status_filter: ArticleStatus | None = Query(None, alias="status"),
    search: str | None = None,
    tags: str | None = None,
    author_id: int | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> ArticleListResponse:
    query = db.query(Article)

    if status_filter:
        query = query.filter(Article.status == status_filter)
    if author_id:
        query = query.filter(Article.author_id == author_id)
    if search:
        like = f"%{search.lower()}%"
        query = query.filter(
            or_(
                func.lower(Article.title).like(like),
                func.lower(Article.body_md).like(like),
            )
        )
    if tags:
        # tags stored as comma separated string
        for tag in [t.strip().lower() for t in tags.split(",") if t.strip()]:
            query = query.filter(func.lower(Article.tags).like(f"%{tag}%"))

    total = query.count()
    articles = (
        query.order_by(Article.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return ArticleListResponse(articles=articles, total=total, page=page, page_size=page_size)


@router.post("", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_article(
    title: str = Form(""),
    body_md: str = Form(""),
    tags: str = Form(""),
    status_value: ArticleStatus = Form(ArticleStatus.DRAFT),
    link_doc: str | None = Form(None),
    link_image: str | None = Form(None),
    file: UploadFile | None = File(None),
    file_image: UploadFile | None = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ArticleResponse:
    normalized_title = title.strip() if isinstance(title, str) else str(title)
    normalized_tags = tags.strip().lower() if isinstance(tags, str) else ""
    slug = _generate_slug(normalized_title)
    slug = _ensure_unique_slug(db, slug)

    article = Article(
        title=normalized_title,
        slug=slug,
        body_md=body_md,
        tags=normalized_tags,
        link_doc=link_doc,
        link_image=link_image,
        status=status_value,
        author_id=current_user.id,
    )

    # Handle file_image upload (specific for images)
    if file_image:
        try:
            storage_service = get_supabase_storage_service()
        except HTTPException as exc:
            if exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
                raise HTTPException(
                    status.HTTP_503_SERVICE_UNAVAILABLE,
                    "Storage Supabase não configurado para upload de arquivos.",
                ) from exc
            raise

        # Validate that file_image is actually an image
        if not file_image.content_type or not file_image.content_type.startswith("image/"):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "O campo file_image deve conter uma imagem (image/*).",
            )

        file_bytes = await file_image.read()
        safe_filename = _sanitize_filename(file_image.filename)
        destination = f"articles/{slug}/images/{safe_filename}"
        stored_path = storage_service.upload_file(
            destination,
            file_bytes,
            content_type=file_image.content_type,
            upsert=True,
        )
        public_url = storage_service.get_public_url(stored_path)
        article.link_image = public_url

    # Handle generic file upload (for documents, etc.)
    if file:
        try:
            storage_service = get_supabase_storage_service()
        except HTTPException as exc:
            if exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
                raise HTTPException(
                    status.HTTP_503_SERVICE_UNAVAILABLE,
                    "Storage Supabase não configurado para upload de arquivos.",
                ) from exc
            raise

        file_bytes = await file.read()
        safe_filename = _sanitize_filename(file.filename)
        destination = f"articles/{slug}/{safe_filename}"
        stored_path = storage_service.upload_file(
            destination,
            file_bytes,
            content_type=file.content_type,
            upsert=True,
        )
        public_url = storage_service.get_public_url(stored_path)
        if file.content_type and file.content_type.startswith("image/"):
            # Only set link_image if not already set by file_image
            if not article.link_image:
                article.link_image = public_url
        else:
            article.link_doc = public_url

    db.add(article)
    db.commit()
    db.refresh(article)
    return article


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(article_id: int, db: Session = Depends(get_db)) -> ArticleResponse:
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artigo não encontrado")
    return article


@router.put("/{article_id}", response_model=ArticleResponse)
def update_article(
    article_id: int,
    data: ArticleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ArticleResponse:
    """Atualiza um artigo (apenas JSON, sem upload de arquivos)"""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artigo não encontrado")

    # Validação: apenas o autor ou admin pode editar
    if article.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para editar este artigo"
        )

    update_data = data.model_dump(exclude_unset=True)

    if "title" in update_data:
        new_slug = _ensure_unique_slug(db, _generate_slug(update_data["title"]), article_id=article.id)
        article.slug = new_slug

    for field, value in update_data.items():
        setattr(article, field, value)

    article.updated_at = datetime.utcnow()
    article.version += 1  # Incrementa a versão
    db.commit()
    db.refresh(article)
    return article


@router.patch("/{article_id}", response_model=ArticleResponse)
async def update_article_with_files(
    article_id: int,
    title: str | None = Form(None),
    body_md: str | None = Form(None),
    tags: str | None = Form(None),
    status_value: ArticleStatus | None = Form(None),
    link_doc: str | None = Form(None),
    link_image: str | None = Form(None),
    file: UploadFile | None = File(None),
    file_image: UploadFile | None = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ArticleResponse:
    """
    Atualiza um artigo com suporte a upload de arquivos.

    - Apenas o autor ou admin pode editar
    - Aceita campos opcionais via multipart/form-data
    - Permite upload de novos arquivos (file) e imagens (file_image)
    """
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artigo não encontrado")

    # Validação: apenas o autor ou admin pode editar
    if article.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para editar este artigo"
        )

    # Atualizar campos de texto
    if title is not None and title.strip():
        article.title = title.strip()
        new_slug = _ensure_unique_slug(db, _generate_slug(article.title), article_id=article.id)
        article.slug = new_slug

    if body_md is not None:
        article.body_md = body_md

    if tags is not None:
        article.tags = tags.strip().lower()

    if status_value is not None:
        article.status = status_value

    if link_doc is not None:
        article.link_doc = link_doc

    if link_image is not None:
        article.link_image = link_image

    # Handle file_image upload (specific for images)
    if file_image:
        try:
            storage_service = get_supabase_storage_service()
        except HTTPException as exc:
            if exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
                raise HTTPException(
                    status.HTTP_503_SERVICE_UNAVAILABLE,
                    "Storage Supabase não configurado para upload de arquivos.",
                ) from exc
            raise

        # Validate that file_image is actually an image
        if not file_image.content_type or not file_image.content_type.startswith("image/"):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "O campo file_image deve conter uma imagem (image/*).",
            )

        file_bytes = await file_image.read()
        safe_filename = _sanitize_filename(file_image.filename)
        destination = f"articles/{article.slug}/images/{safe_filename}"
        stored_path = storage_service.upload_file(
            destination,
            file_bytes,
            content_type=file_image.content_type,
            upsert=True,
        )
        public_url = storage_service.get_public_url(stored_path)
        article.link_image = public_url

    # Handle generic file upload (for documents, etc.)
    if file:
        try:
            storage_service = get_supabase_storage_service()
        except HTTPException as exc:
            if exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
                raise HTTPException(
                    status.HTTP_503_SERVICE_UNAVAILABLE,
                    "Storage Supabase não configurado para upload de arquivos.",
                ) from exc
            raise

        file_bytes = await file.read()
        safe_filename = _sanitize_filename(file.filename)
        destination = f"articles/{article.slug}/{safe_filename}"
        stored_path = storage_service.upload_file(
            destination,
            file_bytes,
            content_type=file.content_type,
            upsert=True,
        )
        public_url = storage_service.get_public_url(stored_path)
        if file.content_type and file.content_type.startswith("image/"):
            # Only set link_image if not already set by file_image
            if not article.link_image:
                article.link_image = public_url
        else:
            article.link_doc = public_url

    article.updated_at = datetime.utcnow()
    article.version += 1
    db.commit()
    db.refresh(article)
    return article


@router.post("/approve", response_model=ArticleApprovalResponse)
def approve_article(
    payload: ApproveArticleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ArticleApprovalResponse:
    article = db.query(Article).filter(Article.id == payload.article_id).first()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artigo não encontrado")

    article.approved_by_id = current_user.id
    article.approved_at = datetime.utcnow()
    article.status = ArticleStatus.APPROVED if payload.approved else ArticleStatus.REJECTED

    if not payload.approved:
        article.tags = article.tags  # no-op, placeholder for future rejection handling

    db.commit()
    db.refresh(article)

    message = (
        "Artigo aprovado com sucesso."
        if payload.approved
        else f"Artigo rejeitado: {payload.reason or 'sem motivo informado'}"
    )

    return ArticleApprovalResponse(
        article_id=article.id,
        status=article.status,
        approved_by_id=current_user.id,
        approved_at=article.approved_at,
        message=message,
    )
