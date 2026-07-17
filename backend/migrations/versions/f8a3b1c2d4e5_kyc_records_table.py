"""kyc records table

Revision ID: f8a3b1c2d4e5
Revises: 4c65be299558
Create Date: 2026-07-17 10:00:00.000000

"""
from typing import Sequence, Union
from sqlalchemy.dialects import postgresql

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f8a3b1c2d4e5'
down_revision: Union[str, Sequence[str], None] = '4c65be299558'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "kyc_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("legal_name", sa.Text, nullable=False),
        sa.Column("aadhaar_number", sa.Text, nullable=False),
        sa.Column("pan_number", sa.Text, nullable=False),
        sa.Column("document_url", sa.Text, nullable=False),
        sa.Column("status", sa.Text, nullable=False, server_default="pending"),
        sa.Column("created_at", sa.TIMESTAMP, nullable=False, server_default=sa.text("now()")),
        sa.Column("verified_at", sa.TIMESTAMP, nullable=True),
    )
    op.create_index("idx_kyc_records_user_id", "kyc_records", ["user_id"])
    op.create_index("idx_kyc_records_status", "kyc_records", ["status"])
    op.execute(
        "ALTER TABLE kyc_records ADD CONSTRAINT kyc_status_check "
        "CHECK (status IN ('pending', 'verified', 'rejected'))"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("kyc_records")
