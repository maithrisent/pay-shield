from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class AuditLog:
    id: UUID
    alias: str
    revealed_user_id: UUID
    requested_by: UUID
    reason: str
    timestamp: datetime
