"""init schema

Revision ID: e4b46e16cc4d
Revises: 
Create Date: 2026-07-16 09:48:53.602017

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql



# revision identifiers, used by Alembic.
revision: str = 'e4b46e16cc4d'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # gen_random_uuid() needs pgcrypto — enable it once, safe to run every time
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # ── users ──────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("phone_hash", sa.Text, nullable=False, unique=True),
        sa.Column(
            "kyc_status", sa.Text, nullable=False, server_default="pending"
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP,
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP,
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.execute(
        "ALTER TABLE users ADD CONSTRAINT kyc_status_check "
        "CHECK (kyc_status IN ('pending', 'verified', 'rejected'))"
    )
 
    # ── wallets ────────────────────────────────────────────
    op.create_table(
        "wallets",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "balance", sa.Integer, nullable=False, server_default="0"
        ),  # paise, never a float
        sa.Column(
            "version", sa.Integer, nullable=False, server_default="0"
        ),  # optimistic locking counter
        sa.Column(
            "updated_at",
            sa.TIMESTAMP,
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("idx_wallets_user_id", "wallets", ["user_id"])
 
    # ── transactions ───────────────────────────────────────
    op.create_table(
        "transactions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "from_wallet_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("wallets.id"),
            nullable=False,
        ),
        sa.Column(
            "to_wallet_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("wallets.id"),
            nullable=False,
        ),
        # No FK constraint yet — the aliases table belongs to Person 2 and
        # may not exist when this migration runs. Add the constraint later
        # in a follow-up migration once that table is in place.
        sa.Column("alias_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("amount", sa.Integer, nullable=False),  # paise
        sa.Column(
            "status", sa.Text, nullable=False, server_default="pending"
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP,
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.execute(
        "ALTER TABLE transactions ADD CONSTRAINT status_check "
        "CHECK (status IN ('pending', 'completed', 'failed'))"
    )
    op.create_index(
        "idx_transactions_from_wallet_id", "transactions", ["from_wallet_id"]
    )
    op.create_index(
        "idx_transactions_to_wallet_id", "transactions", ["to_wallet_id"]
    )


def downgrade():
    # Reverse order — transactions references wallets references users
    op.drop_table("transactions")
    op.drop_table("wallets")
    op.drop_table("users")

