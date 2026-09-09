
"""
Technify VisionAI — Authentication API

Authentication is handled by Supabase.
The backend verifies Supabase access tokens.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import verify_supabase_token


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

bearer_scheme = HTTPBearer(auto_error=False)


# --------------------------------------------------------------------------
# Get current authenticated user
# --------------------------------------------------------------------------

@router.get("/me")
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        bearer_scheme
    ),
):
    """
    Verify the Supabase access token and return the authenticated user.
    """

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = verify_supabase_token(credentials.credentials)

    return {
        "authenticated": True,
        "user_id": str(user.id),
        "email": user.email,
        "role": user.role,
        "app_role": user.app_role,
        "organization_id": (
            str(user.organization_id)
            if user.organization_id
            else None
        ),
    }


# --------------------------------------------------------------------------
# Verify token
# --------------------------------------------------------------------------

@router.post("/verify")
async def verify_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        bearer_scheme
    ),
):
    """
    Verify whether the supplied Supabase access token is valid.
    """

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = verify_supabase_token(credentials.credentials)

    return {
        "valid": True,
        "user_id": str(user.id),
        "email": user.email,
        "role": user.role,
        "app_role": user.app_role,
    }

