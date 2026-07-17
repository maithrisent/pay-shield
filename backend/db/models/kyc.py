from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from typing import Optional


@dataclass
class KycRecord:
    id: UUID
    user_id: UUID
    legal_name: str
    aadhaar_number: str
    pan_number: str
    document_url: str
    status: str  # "pending", "verified", "rejected"
    created_at: datetime
    verified_at: Optional[datetime]
