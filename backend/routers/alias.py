from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth.middleware import get_current_user
from auth.phone_hash import hash_phone
from db.database import get_db_connection
from services.alias_service import get_or_create_alias

router = APIRouter(prefix="/alias", tags=["alias"])

class AliasRequest(BaseModel):
    counterparty_id: str

class AliasResponse(BaseModel):
    alias_string: str

@router.post("/generate", response_model=AliasResponse)
def generate(payload: AliasRequest, current_user: dict = Depends(get_current_user)):
    counterparty_phone_hash = hash_phone(payload.counterparty_phone)
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE phone_hash = %s", (counterparty_phone_hash,))
            row = cur.fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="No user found with that phone number")
            alias_string = get_or_create_alias(cur, current_user["user_id"], row[0])
    return AliasResponse(alias_string=alias_string)