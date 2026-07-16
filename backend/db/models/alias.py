from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from typing import Optional

@dataclass
class Alias:
    id: UUID
    real_user_id: UUID
    counterparty_id: UUID
    alias_string: str
    created_at: datetime
    revoked_at: Optional[datetime]