from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from auth.jwt_handler import verify_jwt

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """
    Attach this to any route with `Depends(get_current_user)` to require
    a valid token before the route runs at all.

    Automatically reads the "Authorization: Bearer <token>" header,
    verifies it via verify_jwt(), and either:
      - returns {user_id, phone_hash} if valid — available inside the
        route as whatever you name the parameter
      - raises 401 Unauthorized if missing, malformed, or expired —
        the route's own code never even runs in that case

    This is what turns verify_jwt() from a standalone function into
    actual middleware — every protected endpoint just adds one line
    instead of manually checking a header and calling verify_jwt itself.
    """
    token = credentials.credentials
    user = verify_jwt(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user