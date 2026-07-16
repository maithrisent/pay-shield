from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth.middleware import get_current_user
from db.database import get_db_connection

router = APIRouter(prefix="/wallet", tags=["wallet"])


class WalletBalanceResponse(BaseModel):
    balance_paise: int
    balance_rupees: float


@router.get("/balance", response_model=WalletBalanceResponse)
def get_balance(current_user: dict = Depends(get_current_user)):
    """
    Protected route — get_current_user only lets this run if the request
    carried a valid token. The user_id used to look up the wallet comes
    entirely from that verified token, never from anything the caller
    could supply directly — so there's no way to pass someone else's
    user_id and see their balance.
    """
    user_id = current_user["user_id"]

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT balance FROM wallets WHERE user_id = %s",
                (user_id,),
            )
            row = cur.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Wallet not found")

    balance_paise = row[0]
    return WalletBalanceResponse(
        balance_paise=balance_paise,
        balance_rupees=balance_paise / 100,
    )