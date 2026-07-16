from fastapi import HTTPException


def debit_wallet(cur, wallet_id: str, amount_paise: int) -> None:
    """
    Subtracts amount_paise from a wallet, using the version column to
    guard against a race condition: if two requests try to debit the
    same wallet at nearly the same instant, only one should win.

    Steps:
      1. Read the current balance and version.
      2. Check there's enough balance to cover the debit.
      3. Update balance and bump version by 1 — but only WHERE the
         version still matches what we just read. If another request
         updated this wallet in between our read and our write, the
         version will have already moved, the WHERE clause matches
         zero rows, and we raise a 409 rather than silently applying
         a debit on top of stale data.

    Must be called with a cursor from an already-open connection
    (not its own get_db_connection() call), so the caller can run
    debit_wallet() and credit_wallet() inside one shared transaction —
    either both changes commit together, or neither does.
    """
    cur.execute(
        "SELECT balance, version FROM wallets WHERE id = %s",
        (wallet_id,),
    )
    row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Wallet not found")

    balance, version = row
    if balance < amount_paise:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    cur.execute(
        """
        UPDATE wallets
        SET balance = balance - %s, version = version + 1, updated_at = now()
        WHERE id = %s AND version = %s
        """,
        (amount_paise, wallet_id, version),
    )
    if cur.rowcount == 0:
        raise HTTPException(
            status_code=409,
            detail="Wallet was updated concurrently, please retry",
        )


def credit_wallet(cur, wallet_id: str, amount_paise: int) -> None:
    """
    Adds amount_paise to a wallet. Same optimistic locking pattern as
    debit_wallet(), minus the balance check — you can always receive
    money, there's no "insufficient" case on the receiving side.
    """
    cur.execute(
        "SELECT version FROM wallets WHERE id = %s",
        (wallet_id,),
    )
    row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Wallet not found")

    version = row[0]

    cur.execute(
        """
        UPDATE wallets
        SET balance = balance + %s, version = version + 1, updated_at = now()
        WHERE id = %s AND version = %s
        """,
        (amount_paise, wallet_id, version),
    )
    if cur.rowcount == 0:
        raise HTTPException(
            status_code=409,
            detail="Wallet was updated concurrently, please retry",
        )