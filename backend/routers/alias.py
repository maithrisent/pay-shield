from fastapi import APIRouter, Depends
from pydantic import BaseModel

from auth.middleware import get_current_user
from db.database import get_db_connection
from services.alias_service import get_or_create_alias

router = APIRouter(prefix="/alias", tags=["alias"])

class AliasRequest(BaseModel):
    counterparty_id: str

class AliasResponse(BaseModel):
    alias_string: str

@router.post("/generate", response_model=AliasResponse)
def generate(payload: AliasRequest, current_user: dict = Depends(get_current_user)):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            alias_string = get_or_create_alias(cur, current_user["user_id"], payload.counterparty_id)
    return AliasResponse(alias_string=alias_string)