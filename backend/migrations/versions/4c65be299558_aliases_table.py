"""aliases table

Revision ID: 4c65be299558
Revises: e4b46e16cc4d
Create Date: 2026-07-16 18:48:16.756278

"""
from typing import Sequence, Union
from sqlalchemy.dialects import postgresql

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4c65be299558'
down_revision: Union[str, Sequence[str], None] = 'e4b46e16cc4d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "aliases",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("real_user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("counterparty_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("alias_string", sa.Text, nullable=False, unique=True),
        sa.Column("created_at", sa.TIMESTAMP, nullable=False, server_default=sa.text("now()")),
        sa.Column("revoked_at", sa.TIMESTAMP, nullable=True),
    )
    op.create_unique_constraint("uq_user_counterparty", "aliases",
                                 ["real_user_id", "counterparty_id"])
    op.create_index("idx_aliases_real_user_id", "aliases", ["real_user_id"])
    op.create_index("idx_aliases_counterparty_id", "aliases", ["counterparty_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("aliases")
