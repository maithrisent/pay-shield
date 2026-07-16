from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from auth.phone_hash import hash_phone
from auth.jwt_handler import create_token
from db.database import get_db_connection

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    phone_number: str


class LoginResponse(BaseModel):
    token: str


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    """
    Demo simplification: no real OTP verification here — any phone
    number that already exists in the users table (i.e. was seeded,
    or would normally have gone through a real signup/KYC flow) can
    log in directly. A production version would verify an OTP before
    ever reaching this point.
    """
    phone_hash = hash_phone(payload.phone_number)

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, phone_hash FROM users WHERE phone_hash = %s",
                (phone_hash,),
            )
            row = cur.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="User not found")

    user_id, stored_phone_hash = row
    token = create_token(user_id=str(user_id), phone_hash=stored_phone_hash)

    return LoginResponse(token=token)