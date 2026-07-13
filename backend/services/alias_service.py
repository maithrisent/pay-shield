import secrets
import string
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from db.models.alias import Alias

class AliasGenerationError(Exception):
    """Raise when unique alias cannot be generated"""
    pass

def generate_alias_string() -> str:
    chars = ( string.ascii_letters + string.digits +"-_" )
    random_part = "".join(secrets.choice(chars) for _ in range(8))
    return f"{random_part}@payshield"