from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from auth.phone_hash import hash_phone
from auth.jwt_handler import create_token
from db.database import get_db_connection
from auth.middleware import get_current_user

import psycopg2.errors

router = APIRouter(prefix="/auth", tags=["auth"])

class SignupRequest(BaseModel):
    phone_number: str
    
class LoginRequest(BaseModel):
    phone_number: str

class SignupResponse(BaseModel):
    token: str
    user_id: str
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

@router.post("/signup", response_model=SignupResponse, status_code=201)
def signup(payload: SignupRequest):
    phone_hash = hash_phone(payload.phone_number)

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users (phone_hash, kyc_status)
                    VALUES (%s, 'pending')
                    RETURNING id
                    """,
                    (phone_hash,),
                )
                user_id = cur.fetchone()[0]

                cur.execute(
                    "INSERT INTO wallets (user_id, balance) VALUES (%s, %s)",
                    (user_id, 0),
                )
    except psycopg2.errors.UniqueViolation:
        # The unique constraint on phone_hash caught a duplicate —
        # this is safer than checking "does this user exist" first,
        # since two simultaneous signups with the same number could
        # otherwise both pass that check before either one inserts.
        raise HTTPException(
            status_code=409,
            detail="An account with this phone number already exists",
        )

    token = create_token(user_id=str(user_id), phone_hash=phone_hash)
    return SignupResponse(token=token, user_id=str(user_id))


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return current_user