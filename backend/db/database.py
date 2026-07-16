import os
from contextlib import contextmanager
from dotenv import load_dotenv
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

# A small pool is plenty at hackathon scale — min=1 keeps one connection
# warm and ready, max=10 gives generous headroom for a few concurrent
# requests without ever opening more than that.
connection_pool = pool.SimpleConnectionPool(1, 10, dsn=DATABASE_URL)


@contextmanager
def get_db_connection():
    """
    Usage:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                row = cur.fetchone()   # comes back as a dict, not a tuple

    Commits automatically if the block finishes without error.
    Rolls back automatically if anything inside the block raises —
    so a payment that fails halfway through never leaves the wallet
    balances in a half-updated state.
    Always returns the connection to the pool when done, whether it
    succeeded or failed.
    """
    conn = connection_pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        connection_pool.putconn(conn)