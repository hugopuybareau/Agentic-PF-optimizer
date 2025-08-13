# backend/app/routers/auth.py

import logging
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from ..auth.dependencies import get_current_user
from ..auth.models.token import Token, TokenRefresh
from ..auth.models.user import UserCreate, UserLogin, UserResponse
from ..auth.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_token,
)
from ..db.base import get_db
from ..db.models import User

logger = logging.getLogger(__name__)
auth_router = APIRouter(prefix="/auth", tags=["authentication"])

_bearer = HTTPBearer()
_bearer_optional = HTTPBearer(auto_error=False)

_SUPPORTED_LANGUAGES = {"en", "fr"}


@auth_router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_data: UserCreate,
    db: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    existing = (
        db.query(User)
        .filter(
            (User.email == user_data.email)
            | (User.username == user_data.username)
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered",
        )

    hashed = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed,
        full_name=user_data.full_name,
        preferred_language=user_data.preferred_language or "en",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@auth_router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    db: Annotated[Session, Depends(get_db)],
) -> Token:
    user = db.query(User).filter(User.email == user_credentials.email).first()
    if (
        not user
        or not verify_password(
            user_credentials.password, getattr(user, "hashed_password", "")
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not getattr(user, "is_active", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    user.last_login = datetime.now(UTC)
    db.commit()

    return Token(
        access_token=create_access_token(data={"sub": str(user.id)}),
        refresh_token=create_refresh_token(data={"sub": str(user.id)}),
        token_type="bearer",
    )


@auth_router.post("/refresh", response_model=Token)
async def refresh(
    token_data: TokenRefresh,
    db: Annotated[Session, Depends(get_db)],
) -> Token:
    user_id = verify_token(token_data.refresh_token, token_type="refresh")
    user = db.query(User).filter(User.id == user_id).first()

    if not user or not getattr(user, "is_active", False):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    return Token(
        access_token=create_access_token(data={"sub": str(user.id)}),
        refresh_token=create_refresh_token(data={"sub": str(user.id)}),
        token_type="bearer",
    )


@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    logger.info("AUTH_ME: request received at %s", datetime.utcnow())
    return current_user


@auth_router.patch("/me/language", response_model=UserResponse)
async def update_preferred_language(
    preferred_language: Annotated[str, Body(..., embed=True)],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    if preferred_language not in _SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported language: {preferred_language}",
        )

    current_user.preferred_language = preferred_language
    db.commit()
    db.refresh(current_user)
    return current_user
