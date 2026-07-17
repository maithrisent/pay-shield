from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from auth.middleware import get_current_user
from auth.phone_hash import hash_phone
from db.database import get_db_connection
from services.wallet_service import debit_wallet, credit_wallet
from services.alias_service import get_or_create_alias

from services.alias_service import resolve_alias #added my maithri
from services.payment_orchestrator import (
    validate_payer,
    validate_payee,
    create_payment,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])


class PaymentRequest(BaseModel):
    to_phone_number: str
    amount_paise: int = Field(gt=0)  # rejects zero or negative amounts up front


class PaymentResponse(BaseModel):
    transaction_id: str
    status: str
    amount_paise: int

class PayByAliasRequest(BaseModel): #added my maithri
    alias_string: str
    amount_paise: int = Field(gt=0)

class ReceiptResponse(BaseModel):  # <-- add it here
    transaction_id: str
    amount_paise: int
    status: str
    created_at: str


@router.post("/pay", response_model=PaymentResponse)
def pay(
    payload: PaymentRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Sender is always taken from the verified token, never from the
    request body — same principle as /wallet/balance. The recipient
    is resolved by hashing their phone number the same way signup/login
    already do, so no raw phone number is ever compared directly.

    Everything below runs inside one get_db_connection() block, so a
    debit that succeeds but a credit that fails (or vice versa) rolls
    both back together instead of leaving money in limbo.
    """
    sender_user_id = current_user["user_id"]
    recipient_phone_hash = hash_phone(payload.to_phone_number)

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM users WHERE phone_hash = %s",
                (recipient_phone_hash,),
            )
            recipient_row = cur.fetchone()
            if recipient_row is None:
                raise HTTPException(status_code=404, detail="Recipient not found")
            recipient_user_id = recipient_row[0]

            if str(recipient_user_id) == sender_user_id:
                raise HTTPException(status_code=400, detail="Cannot pay yourself")

            payer_alias = get_or_create_alias(cur, sender_user_id, recipient_user_id)
            
            cur.execute(
                "SELECT id FROM wallets WHERE user_id = %s",
                (sender_user_id,),
            )
            sender_wallet_row = cur.fetchone()
            if sender_wallet_row is None:
                raise HTTPException(status_code=404, detail="Sender wallet not found")
            sender_wallet_id = sender_wallet_row[0]

            cur.execute(
                "SELECT id FROM wallets WHERE user_id = %s",
                (recipient_user_id,),
            )
            recipient_wallet_row = cur.fetchone()
            if recipient_wallet_row is None:
                raise HTTPException(status_code=404, detail="Recipient wallet not found")
            recipient_wallet_id = recipient_wallet_row[0]

            # Move the money — debit_wallet raises 400 on insufficient
            # balance, or 409 if a concurrent update is detected via the
            # version column. Either way, nothing below this line runs,
            # and get_db_connection() rolls back cleanly.
            debit_wallet(cur, sender_wallet_id, payload.amount_paise)
            credit_wallet(cur, recipient_wallet_id, payload.amount_paise)

            cur.execute(
                """
                INSERT INTO transactions (from_wallet_id, to_wallet_id, amount, status)
                VALUES (%s, %s, %s, 'completed')
                RETURNING id
                """,
                (sender_wallet_id, recipient_wallet_id, payload.amount_paise, payer_alias),
            )
            transaction_id = cur.fetchone()[0]

    return PaymentResponse(
        transaction_id=str(transaction_id),
        status="completed",
        amount_paise=payload.amount_paise,
    )

@router.post("/pay-by-alias", response_model=PaymentResponse) #added my maithri
def pay_by_alias(
    payload: PayByAliasRequest,
    current_user: dict = Depends(get_current_user),
):
    sender_user_id = current_user["user_id"]

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            recipient_user_id = resolve_alias(cur, payload.alias_string)

            if str(recipient_user_id) == sender_user_id:
                raise HTTPException(status_code=400, detail="Cannot pay yourself")

            sender_wallet_id = validate_payer(cur, sender_user_id)
            recipient_wallet_id = validate_payee(cur, recipient_user_id)

            transaction_id = create_payment(
                cur,
                sender_wallet_id,
                recipient_wallet_id,
                payload.amount_paise,
            )

    return PaymentResponse(
        transaction_id=str(transaction_id),
        status="completed",
        amount_paise=payload.amount_paise,
    )

@router.get("/{transaction_id}/receipt", response_model=ReceiptResponse)
def get_receipt(transaction_id: str, current_user: dict = Depends(get_current_user)):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, amount, status, created_at FROM transactions WHERE id = %s",
                (transaction_id,),
            )
            row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return ReceiptResponse(
        transaction_id=str(row[0]), amount_paise=row[1],
        status=row[2], created_at=row[3].isoformat(),
    )