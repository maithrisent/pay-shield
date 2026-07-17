from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from uuid import UUID

from auth.middleware import get_current_user
from auth.middleware import bearer_scheme
from fastapi.security import HTTPAuthorizationCredentials
from db.database import get_db_connection

router = APIRouter(prefix="/compliance", tags=["compliance"])


def get_admin_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """
    Admin-only middleware. Verifies JWT token and checks is_admin flag.
    Raises 403 Forbidden if user is not an admin.
    """
    current_user = get_current_user(credentials)
    user_id = current_user["user_id"]
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT is_admin FROM users WHERE id = %s", (user_id,))
            admin_row = cur.fetchone()
            if admin_row is None or not admin_row[0]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only admin users can access this resource"
                )
    
    return current_user


class KycUploadRequest(BaseModel):
    legal_name: str = Field(..., min_length=1)
    aadhaar_number: str = Field(..., min_length=1)
    pan_number: str = Field(..., min_length=1)
    document_url: str = Field(..., min_length=1)


class KycUploadResponse(BaseModel):
    success: bool
    status: str


class KycVerifyRequest(BaseModel):
    user_id: UUID


class KycVerifyResponse(BaseModel):
    success: bool
    status: str


class KycStatusResponse(BaseModel):
    status: str


class DiscloseRequest(BaseModel):
    alias: str = Field(..., min_length=1)
    reason: str = Field(..., min_length=1)


class DiscloseResponse(BaseModel):
    legal_name: str
    aadhaar_number: str
    pan_number: str


class AuditLogEntry(BaseModel):
    timestamp: str
    requested_by: str
    alias: str
    reason: str
    revealed_user_id: str


class AuditLogsResponse(BaseModel):
    entries: list[AuditLogEntry]
    total: int


@router.post("/kyc/upload", response_model=KycUploadResponse, status_code=201)
def kyc_upload(
    payload: KycUploadRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Upload KYC documents for verification.
    Authenticated users only.
    """
    user_id = current_user["user_id"]
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO kyc_records 
                       (user_id, legal_name, aadhaar_number, pan_number, document_url, status)
                       VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (user_id, payload.legal_name, payload.aadhaar_number, 
                     payload.pan_number, payload.document_url, "pending")
                )
        return KycUploadResponse(success=True, status="pending")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to upload KYC documents"
        )


@router.post("/kyc/verify", response_model=KycVerifyResponse)
def kyc_verify(
    payload: KycVerifyRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Verify KYC for a user (mock implementation for MVP).
    Authenticated users only (admin can verify for others).
    Updates KYC record status to verified.
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Update KYC record
                cur.execute(
                    """UPDATE kyc_records 
                       SET status = %s, verified_at = now()
                       WHERE user_id = %s
                    """,
                    ("verified", str(payload.user_id))
                )
                
                # Check if any row was updated
                if cur.rowcount == 0:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="KYC record not found for this user"
                    )
        
        return KycVerifyResponse(success=True, status="verified")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to verify KYC"
        )


@router.get("/kyc/status", response_model=KycStatusResponse)
def kyc_status(current_user: dict = Depends(get_current_user)):
    """
    Get the current user's KYC verification status.
    Authenticated users only.
    """
    user_id = current_user["user_id"]
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT status FROM kyc_records 
                   WHERE user_id = %s
                   ORDER BY created_at DESC
                   LIMIT 1
                """,
                (user_id,)
            )
            row = cur.fetchone()
    
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No KYC record found for this user"
        )
    
    return KycStatusResponse(status=row[0])



@router.post("/disclose", response_model=DiscloseResponse)
def disclose(
    payload: DiscloseRequest,
    current_admin: dict = Depends(get_admin_user)
):
    """
    Disclose verified KYC information for an alias.
    Admin users only. Creates an audit log entry for compliance.
    """
    admin_user_id = current_admin["user_id"]
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Resolve alias to user_id
            cur.execute(
                "SELECT real_user_id FROM aliases WHERE alias_string = %s",
                (payload.alias,)
            )
            alias_row = cur.fetchone()
            if alias_row is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Alias not found"
                )
            
            revealed_user_id = alias_row[0]
            
            # Fetch verified KYC record
            cur.execute(
                """SELECT legal_name, aadhaar_number, pan_number FROM kyc_records 
                   WHERE user_id = %s AND status = 'verified'
                   ORDER BY verified_at DESC
                   LIMIT 1
                """,
                (revealed_user_id,)
            )
            kyc_row = cur.fetchone()
            if kyc_row is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Verified KYC record not found for this user"
                )
            
            legal_name, aadhaar_number, pan_number = kyc_row
            
            # Create audit log entry
            cur.execute(
                """INSERT INTO audit_logs 
                   (alias, revealed_user_id, requested_by, reason)
                   VALUES (%s, %s, %s, %s)
                """,
                (payload.alias, revealed_user_id, admin_user_id, payload.reason)
            )
    
    return DiscloseResponse(
        legal_name=legal_name,
        aadhaar_number=aadhaar_number,
        pan_number=pan_number
    )



@router.get("/audit", response_model=AuditLogsResponse)
def audit_logs(
    current_admin: dict = Depends(get_admin_user),
    skip: int = 0,
    limit: int = 50
):
    """
    Get audit log entries. Admin users only.
    Returns paginated results ordered by timestamp (newest first).
    """
    # Validate pagination parameters
    if skip < 0:
        skip = 0
    if limit < 1:
        limit = 1
    if limit > 500:
        limit = 500  # Max 500 per page
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Get total count
            cur.execute("SELECT COUNT(*) FROM audit_logs")
            total_count = cur.fetchone()[0]
            
            # Fetch paginated audit logs
            cur.execute(
                """SELECT timestamp, requested_by, alias, reason, revealed_user_id 
                   FROM audit_logs 
                   ORDER BY timestamp DESC
                   LIMIT %s OFFSET %s
                """,
                (limit, skip)
            )
            rows = cur.fetchall()
    
    entries = [
        AuditLogEntry(
            timestamp=str(row[0]),
            requested_by=str(row[1]),
            alias=row[2],
            reason=row[3],
            revealed_user_id=str(row[4])
        )
        for row in rows
    ]
    
    return AuditLogsResponse(entries=entries, total=total_count)



