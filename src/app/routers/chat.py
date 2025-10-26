from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..db import get_db
from ..dependencies import get_current_user, get_optional_user
from ..models.chat import Chat, ChatMessage
from ..models.user import User
from ..schemas.chat import (
    ChatCreate,
    ChatListResponse,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatRatingCreate,
    ChatRatingResponse,
    ChatRatingStatsResponse,
    ChatResponse,
    ChatUpdate,
    ChatWithMessagesResponse,
)

router = APIRouter(prefix="/chats", tags=["chats"])


# =============== CRUD de Chats ===============

@router.post("", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
def create_chat(
    data: ChatCreate,
    current_user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
) -> ChatResponse:
    """
    Cria um novo chat.

    - Se autenticado: cria chat associado ao user_id
    - Se anônimo: cria chat com session_id
    """
    chat = Chat(
        user_id=current_user.id if current_user else None,
        session_id=data.session_id if not current_user else None,
        title=data.title,
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat


@router.get("", response_model=ChatListResponse)
def list_chats(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session_id: str | None = None,
    current_user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
) -> ChatListResponse:
    """
    Lista chats do usuário autenticado ou da sessão anônima.
    """
    query = db.query(Chat)

    if current_user:
        query = query.filter(Chat.user_id == current_user.id)
    elif session_id:
        query = query.filter(Chat.session_id == session_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Forneça session_id ou autentique-se",
        )

    total = query.count()
    chats = (
        query.order_by(Chat.updated_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return ChatListResponse(chats=chats, total=total, page=page, page_size=page_size)


@router.get("/{chat_id}", response_model=ChatWithMessagesResponse)
def get_chat(
    chat_id: int,
    current_user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
) -> ChatWithMessagesResponse:
    """Retorna um chat com todo o histórico de mensagens."""
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat não encontrado")

    # Validar acesso
    if current_user and chat.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem acesso a este chat",
        )

    return chat


@router.patch("/{chat_id}", response_model=ChatResponse)
def update_chat(
    chat_id: int,
    data: ChatUpdate,
    current_user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
) -> ChatResponse:
    """Atualiza informações do chat (título, summary, etc)."""
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat não encontrado")

    # Validar acesso
    if current_user and chat.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem acesso a este chat",
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(chat, field, value)

    chat.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(chat)
    return chat


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat(
    chat_id: int,
    current_user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """Deleta um chat e todas as suas mensagens."""
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat não encontrado")

    # Validar acesso
    if current_user and chat.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem acesso a este chat",
        )

    db.delete(chat)
    db.commit()


# =============== Mensagens ===============

@router.post("/{chat_id}/messages", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
def create_message(
    chat_id: int,
    data: ChatMessageCreate,
    current_user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
) -> ChatMessageResponse:
    """Adiciona uma nova mensagem ao chat."""
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat não encontrado")

    # Validar acesso
    if current_user and chat.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem acesso a este chat",
        )

    message = ChatMessage(
        chat_id=chat_id,
        role=data.role,
        content=data.content,
    )

    db.add(message)
    chat.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(message)
    return message


@router.get("/{chat_id}/messages", response_model=list[ChatMessageResponse])
def list_messages(
    chat_id: int,
    limit: int = Query(100, ge=1, le=500),
    current_user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
) -> list[ChatMessageResponse]:
    """Lista mensagens de um chat."""
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat não encontrado")

    # Validar acesso
    if current_user and chat.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem acesso a este chat",
        )

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.chat_id == chat_id)
        .order_by(ChatMessage.created_at.asc())
        .limit(limit)
        .all()
    )

    return messages


# =============== Sistema de Avaliação (Rating) ===============

@router.post("/{chat_id}/rating", response_model=ChatRatingResponse)
def rate_chat(
    chat_id: int,
    data: ChatRatingCreate,
    current_user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
) -> ChatRatingResponse:
    """
    Avalia uma conversa com nota de 0 a 5.

    - Permite re-avaliar (atualiza a nota anterior)
    - Pode ser usado por usuários autenticados ou anônimos (com acesso ao chat)
    """
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat não encontrado")

    # Validar acesso
    if current_user and chat.user_id and chat.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem acesso a este chat",
        )

    # Atualizar rating
    chat.rating = data.rating
    chat.rating_comment = data.comment
    chat.rated_at = datetime.utcnow()
    chat.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(chat)

    message = "Avaliação atualizada com sucesso" if chat.rated_at else "Avaliação registrada com sucesso"

    return ChatRatingResponse(
        chat_id=chat.id,
        rating=chat.rating,
        rating_comment=chat.rating_comment,
        rated_at=chat.rated_at,
        message=message,
    )


@router.get("/stats/ratings", response_model=ChatRatingStatsResponse)
def get_rating_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatRatingStatsResponse:
    """
    Retorna estatísticas de avaliações de todos os chats.

    - Média geral de avaliações
    - Distribuição de notas (0-5)
    - Total de chats avaliados vs total de chats
    - Requer autenticação de admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem ver estatísticas gerais",
        )

    # Total de chats
    total_chats = db.query(Chat).count()

    # Chats com rating
    rated_chats = db.query(Chat).filter(Chat.rating.isnot(None)).all()
    total_ratings = len(rated_chats)

    if total_ratings == 0:
        return ChatRatingStatsResponse(
            total_ratings=0,
            average_rating=0.0,
            rating_distribution={0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
            total_chats=total_chats,
            percentage_rated=0.0,
        )

    # Calcular média
    average_rating = sum(chat.rating for chat in rated_chats) / total_ratings

    # Distribuição de ratings
    rating_distribution = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for chat in rated_chats:
        rating_distribution[chat.rating] += 1

    # Porcentagem de chats avaliados
    percentage_rated = (total_ratings / total_chats * 100) if total_chats > 0 else 0.0

    return ChatRatingStatsResponse(
        total_ratings=total_ratings,
        average_rating=round(average_rating, 2),
        rating_distribution=rating_distribution,
        total_chats=total_chats,
        percentage_rated=round(percentage_rated, 2),
    )


@router.get("/user/ratings", response_model=ChatRatingStatsResponse)
def get_user_rating_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatRatingStatsResponse:
    """
    Retorna estatísticas de avaliações dos chats do usuário atual.

    - Média das avaliações dos chats do usuário
    - Distribuição de notas
    - Total de chats do usuário avaliados vs total
    """
    # Total de chats do usuário
    total_chats = db.query(Chat).filter(Chat.user_id == current_user.id).count()

    # Chats do usuário com rating
    rated_chats = (
        db.query(Chat)
        .filter(Chat.user_id == current_user.id, Chat.rating.isnot(None))
        .all()
    )
    total_ratings = len(rated_chats)

    if total_ratings == 0:
        return ChatRatingStatsResponse(
            total_ratings=0,
            average_rating=0.0,
            rating_distribution={0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
            total_chats=total_chats,
            percentage_rated=0.0,
        )

    # Calcular média
    average_rating = sum(chat.rating for chat in rated_chats) / total_ratings

    # Distribuição de ratings
    rating_distribution = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for chat in rated_chats:
        rating_distribution[chat.rating] += 1

    # Porcentagem de chats avaliados
    percentage_rated = (total_ratings / total_chats * 100) if total_chats > 0 else 0.0

    return ChatRatingStatsResponse(
        total_ratings=total_ratings,
        average_rating=round(average_rating, 2),
        rating_distribution=rating_distribution,
        total_chats=total_chats,
        percentage_rated=round(percentage_rated, 2),
    )
