from dotenv import load_dotenv
load_dotenv()

import os
import uuid
import pytest
import psycopg2
from fastapi.testclient import TestClient

from main import app
from auth.phone_hash import hash_phone
from auth.jwt_handler import create_token
from services.alias_service import get_or_create_alias


@pytest.fixture
def db_conn():
    """One real connection to the database, open for the whole test."""
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    yield conn
    conn.close()


@pytest.fixture
def db_cursor(db_conn):
    cur = db_conn.cursor()
    yield cur
    cur.close()


def _create_user(cur, phone_number, balance_paise=0):
    """Same shape as seed.py — insert a user, then a wallet for them."""
    phone_hash = hash_phone(phone_number)
    cur.execute(
        "INSERT INTO users (phone_hash, kyc_status) VALUES (%s, 'verified') RETURNING id",
        (phone_hash,),
    )
    user_id = cur.fetchone()[0]
    cur.execute(
        "INSERT INTO wallets (user_id, balance) VALUES (%s, %s)",
        (user_id, balance_paise),
    )
    return user_id


@pytest.fixture
def user_a(db_conn, db_cursor):
    phone = f"9{uuid.uuid4().int % 10**9:09d}"
    user_id = _create_user(db_cursor, phone, balance_paise=500000)
    db_conn.commit()
    yield str(user_id)
    db_cursor.execute(
        """DELETE FROM transactions WHERE from_wallet_id IN
           (SELECT id FROM wallets WHERE user_id = %s)
           OR to_wallet_id IN (SELECT id FROM wallets WHERE user_id = %s)""",
        (user_id, user_id),
    )
    db_cursor.execute("DELETE FROM wallets WHERE user_id = %s", (user_id,))
    db_cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    db_conn.commit()


@pytest.fixture
def user_b(db_conn, db_cursor):
    phone = f"9{uuid.uuid4().int % 10**9:09d}"
    user_id = _create_user(db_cursor, phone, balance_paise=0)
    db_conn.commit()
    yield str(user_id)
    db_cursor.execute(
        """DELETE FROM transactions WHERE from_wallet_id IN
           (SELECT id FROM wallets WHERE user_id = %s)
           OR to_wallet_id IN (SELECT id FROM wallets WHERE user_id = %s)""",
        (user_id, user_id),
    )
    db_cursor.execute("DELETE FROM wallets WHERE user_id = %s", (user_id,))
    db_cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    db_conn.commit()


@pytest.fixture
def client():
    """Lets tests call your API endpoints without actually running a server."""
    return TestClient(app)


@pytest.fixture
def auth_headers(user_a):
    """A valid login token for user_a, formatted the way a real request needs it."""
    token = create_token(user_id=user_a, phone_hash="test-phone-hash")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def alias_string(db_conn, db_cursor, user_a, user_b):
    """An alias belonging to user_b, so user_a (the payer) can pay through it."""
    alias = get_or_create_alias(db_cursor, user_b, user_a)  # <-- swapped: user_b is real_user_id now
    db_conn.commit()
    yield alias
    db_cursor.execute("DELETE FROM aliases WHERE alias_string = %s", (alias,))
    db_conn.commit()