"""audit logs table

Revision ID: a1b2c3d4e5f6
Revises: f8a3b1c2d4e5
Create Date: 2026-07-17 10:30:00.000000

"""
from typing import Sequence, Union
from sqlalchemy.dialects import postgresql

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'f8a3b1c2d4e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("alias", sa.Text, nullable=False),
        sa.Column("revealed_user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("requested_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reason", sa.Text, nullable=False),
        sa.Column("timestamp", sa.TIMESTAMP, nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_audit_logs_revealed_user_id", "audit_logs", ["revealed_user_id"])
    op.create_index("idx_audit_logs_requested_by", "audit_logs", ["requested_by"])
    op.create_index("idx_audit_logs_timestamp", "audit_logs", ["timestamp"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("audit_logs")
