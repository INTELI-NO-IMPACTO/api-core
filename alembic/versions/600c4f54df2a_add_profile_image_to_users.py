"""add_profile_image_to_users

Revision ID: 600c4f54df2a
Revises: a7139272e46b
Create Date: 2025-10-26 09:20:50.698096

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '600c4f54df2a'
down_revision: Union[str, None] = 'a7139272e46b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Adiciona coluna profile_image_url à tabela users
    op.add_column('users', sa.Column('profile_image_url', sa.String(length=500), nullable=True))


def downgrade() -> None:
    # Remove coluna profile_image_url da tabela users
    op.drop_column('users', 'profile_image_url')
