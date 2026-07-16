import os
import jwt
from datetime import datetime, timedelta, timezone

# Loaded from .env — same JWT_SECRET must be used everywhere a token
# gets signed or verified. Never commit the actual value.
JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 2


def create_token(user_id: str, phone_hash: str) -> str:
    """
    Called at login. Issues a signed token containing only the two
    fields the contract allows — never legal_name, never phone_number
    in plaintext.
    """
    now = datetime.now(timezone.utc)
    payload = {
        "user_id": user_id,
        "phone_hash": phone_hash,
        "iat": now,                              # issued-at, standard claim
        "exp": now + timedelta(hours=JWT_EXPIRY_HOURS),  # expiry, standard claim
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_jwt(token: str) -> dict | None:
    """
    Matches CONTRACT.md exactly:
    verifyJWT(token) -> { user_id: string, phone_hash: string } | null

    Every other service in the system should treat this function as
    the only source of truth for "is this request really from who it
    claims to be."
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {
            "user_id": payload["user_id"],
            "phone_hash": payload["phone_hash"],
        }
    except jwt.ExpiredSignatureError:
        # Token was valid once but its exp time has passed
        return None
    except jwt.InvalidTokenError:
        # Covers a bad signature, malformed token, tampered payload —
        # collapsing every failure mode into the single null case the
        # contract promises, so callers never need to know *why* it failed
        return None