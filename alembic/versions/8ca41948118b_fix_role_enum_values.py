"""fix role enum values

Revision ID: 8ca41948118b
Revises: da4eb41a29fa
Create Date: 2025-10-26 04:56:35.337931

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ca41948118b'
down_revision: Union[str, None] = 'da4eb41a29fa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop and recreate the role enum with correct values
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE VARCHAR(50)")
    op.execute("DROP TYPE IF EXISTS role")
    op.execute("CREATE TYPE role AS ENUM ('beneficiario', 'assistente', 'admin')")
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE role USING role::role")


def downgrade() -> None:
    # Revert to old enum values
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE VARCHAR(50)")
    op.execute("DROP TYPE IF EXISTS role")
    op.execute("CREATE TYPE role AS ENUM ('USER', 'ASSISTANT', 'ADMIN')")
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE role USING role::role")
