# backend/app/auth/dependencies.py

import logging
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ..db.base import get_db
from ..db.models import User
from .security import verify_token

logger = logging.getLogger(__name__)

_bearer_scheme = HTTPBearer()
_bearer_scheme_optional = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:

    """
    standard, strict authentication dependency.
    requires a valid token, finds the user in DB, and ensures the user is active.
    401 if no user is found or token is missing/bad
    400 if user is inactive
    use for protected routes where auth is required.
    """

    token = credentials.credentials
    user_id = verify_token(token)

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.is_active is not True:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    return user

async def get_current_user_optional(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme_optional)],
    db: Annotated[Session, Depends(get_db)],
) -> User | None:

    """
    does not require a token, but if provided, verifies it.
    never raises if missing/invalid token; always returns User | None.
    use for routes where auth is optional.
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials
        user_id = verify_token(token)

        user = db.query(User).filter(User.id == user_id).first()
        if user is not None and getattr(user, "is_active", False) is True:
            return user
        return None
    except Exception as e:
        logger.warning(f"Token verification failed: {e}")
        return None
