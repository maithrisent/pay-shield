import secrets, string
from fastapi import HTTPException
from psycopg2.errors import UniqueViolation

def generate_alias_string() -> str:
    # makes something like "aB3-x9Qz@payshield"
    chars = string.ascii_letters + string.digits + "-_"
    random_part = "".join(secrets.choice(chars) for _ in range(8))
    return f"{random_part}@payshield"

def lookup_alias(cur, real_user_id: str, counterparty_id: str) -> str | None:
    # checks: does this pair of people already have an alias?
    cur.execute(
        """SELECT alias_string FROM aliases
           WHERE real_user_id = %s AND counterparty_id = %s AND revoked_at IS NULL""",
        (real_user_id, counterparty_id),
    )
    row = cur.fetchone()
    return row[0] if row else None

def get_or_create_alias(cur, real_user_id: str, counterparty_id: str) -> str:
    # if one already exists, reuse it. otherwise, make a new one.
    existing = lookup_alias(cur, real_user_id, counterparty_id)
    if existing:
        return existing

    for _ in range(5):  # try a few times in case of a very rare duplicate
        alias_string = generate_alias_string()
        try:
            cur.execute(
                """INSERT INTO aliases (real_user_id, counterparty_id, alias_string)
                   VALUES (%s, %s, %s)""",
                (real_user_id, counterparty_id, alias_string),
            )
            return alias_string
        except UniqueViolation:
            continue
    raise HTTPException(status_code=500, detail="Could not generate a unique alias")

def resolve_alias(cur, alias_string: str) -> str:
    # turns an alias like "aB3-x9Qz@payshield" back into the real user's ID
    cur.execute(
        "SELECT real_user_id FROM aliases WHERE alias_string = %s AND revoked_at IS NULL",
        (alias_string,),
    )
    row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Alias not found or revoked")
    return row[0]