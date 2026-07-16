from fastapi import HTTPException
from services.wallet_service import debit_wallet, credit_wallet

def validate_payer(cur, user_id: str) -> str:
    # makes sure the person paying actually has a wallet, returns its ID
    cur.execute("SELECT id FROM wallets WHERE user_id = %s", (user_id,))
    row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Sender wallet not found")
    return row[0]

def validate_payee(cur, real_user_id: str) -> str:
    # same thing, but for the person receiving money
    cur.execute("SELECT id FROM wallets WHERE user_id = %s", (real_user_id,))
    row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Recipient wallet not found")
    return row[0]

def create_payment(cur, sender_wallet_id: str, recipient_wallet_id: str,
                    amount_paise: int, alias_id: str | None = None) -> str:
    # actually moves the money and writes down that it happened
    debit_wallet(cur, sender_wallet_id, amount_paise)
    credit_wallet(cur, recipient_wallet_id, amount_paise)
    cur.execute(
        """INSERT INTO transactions (from_wallet_id, to_wallet_id, amount, status, alias_id)
           VALUES (%s, %s, %s, 'completed', %s) RETURNING id""",
        (sender_wallet_id, recipient_wallet_id, amount_paise, alias_id),
    )
    return cur.fetchone()[0]