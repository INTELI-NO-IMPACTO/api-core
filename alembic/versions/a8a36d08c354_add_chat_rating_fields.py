"""add_chat_rating_fields

Revision ID: a8a36d08c354
Revises: 600c4f54df2a
Create Date: 2025-10-26 11:05:40.064437

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a8a36d08c354'
down_revision: Union[str, None] = '600c4f54df2a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Adicionar campos de rating na tabela chats
    op.add_column('chats', sa.Column('rating', sa.Integer(), nullable=True))
    op.add_column('chats', sa.Column('rating_comment', sa.Text(), nullable=True))
    op.add_column('chats', sa.Column('rated_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # Remover campos de rating
    op.drop_column('chats', 'rated_at')
    op.drop_column('chats', 'rating_comment')
    op.drop_column('chats', 'rating')
