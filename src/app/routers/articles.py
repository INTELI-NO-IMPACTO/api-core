from datetime import datetime

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
from ..dependencies import get_current_user, require_admin
from ..models.article import Article, ArticleStatus
from ..models.user import Role, User
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
    title: str = Form(...),
    body_md: str = Form(...),
    tags: str = Form(...),
    status_value: ArticleStatus = Form(ArticleStatus.DRAFT),
    link_doc: str | None = Form(None),
    link_image: str | None = Form(None),
    file: UploadFile | None = File(None),
    file_image: UploadFile | None = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ArticleResponse:
    if len(title.strip()) < 3:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Título deve ter no mínimo 3 caracteres.")
    if not tags or not tags.strip():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Pelo menos uma tag é obrigatória.")

    normalized_tags = tags.strip().lower()
    slug = _generate_slug(title)
    slug = _ensure_unique_slug(db, slug)

    article = Article(
        title=title,
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
        destination = f"articles/{slug}/images/{file_image.filename}"
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
        destination = f"articles/{slug}/{file.filename}"
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
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artigo não encontrado")

    if current_user.role not in {Role.ADMIN, Role.ASSISTENTE} and article.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário sem permissão para editar este artigo",
        )

    update_data = data.model_dump(exclude_unset=True)

    if "title" in update_data:
        new_slug = _ensure_unique_slug(db, _generate_slug(update_data["title"]), article_id=article.id)
        article.slug = new_slug

    for field, value in update_data.items():
        setattr(article, field, value)

    article.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(article)
    return article


@router.post("/approve", response_model=ArticleApprovalResponse)
def approve_article(
    payload: ApproveArticleRequest,
    current_user: User = Depends(require_admin),
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
