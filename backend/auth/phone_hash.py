import os
import hmac
import hashlib
from dotenv import load_dotenv

load_dotenv()

PHONE_HASH_SECRET = os.environ["PHONE_HASH_SECRET"]


def hash_phone(phone_number: str) -> str:
    """
    HMAC, not a plain hash — a bare SHA256 of a phone number is crackable
    by brute force since phone numbers are a small, guessable space.
    HMAC requires knowing PHONE_HASH_SECRET too, which makes that
    precomputation attack infeasible.

    Must be called identically everywhere a phone number needs to become
    a lookup key — seeding, login, anywhere else that checks "does this
    phone number already exist."
    """
    return hmac.new(
        PHONE_HASH_SECRET.encode(),
        phone_number.encode(),
        hashlib.sha256,
    ).hexdigest()