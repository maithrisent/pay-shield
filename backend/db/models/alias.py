import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from db.database import Base
from datetime import datetime, UTC


class Alias(Base):
    __tablename__ = "aliases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    real_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    counterparty_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    alias_string = Column(String, unique=True, nullable=False)

    created_at = Column(DateTime(timezone=True),
                        default=lambda: datetime.now(UTC))
    revoked_at = Column(
        DateTime(timezone=True),
        nullable=True
    )
    __table_args__ = (
        UniqueConstraint("real_user_id", "counterparty_id", name="uq_user_counterparty"),
        Index("idx_aliases_real_user_id", "real_user_id"),
        Index("idx_aliases_counterparty_id", "counterparty_id"),
    )

    @property
    def is_active(self) -> bool:
        return self.revoked_at is None
    
    def __repr__(self):
        return f"<Alias {self.alias_string} ({self.real_user_id} -> {self.counterparty_id})>"