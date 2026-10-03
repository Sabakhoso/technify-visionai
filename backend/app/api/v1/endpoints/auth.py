"""
Technify VisionAI — Authentication API

Authentication is handled by Supabase.
The backend verifies Supabase access tokens, and — for public self-serve
signup — provisions new organizations + their first admin user using the
service-role Supabase client (never exposed to the frontend).
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.security import verify_supabase_token
from app.integrations.supabase_client import admin_create_user, SupabaseOperationError
from app.models.organization import Organization
from app.schemas.auth import RegisterRequest, RegisterResponse
from app.utils.helpers import slugify


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
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
):
    """Verify the Supabase access token and return the authenticated user."""

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
        "organization_id": str(user.organization_id) if user.organization_id else None,
    }


# --------------------------------------------------------------------------
# Verify token
# --------------------------------------------------------------------------

@router.post("/verify")
async def verify_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
):
    """Verify whether the supplied Supabase access token is valid."""

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


# --------------------------------------------------------------------------
# Register — public self-serve signup (creates org + first admin user)
# --------------------------------------------------------------------------

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Creates a new organization and its first admin user in one step.
    Public endpoint — no Bearer token required, since the user doesn't
    exist yet. Uses the service-role Supabase client server-side only.
    """
    slug = slugify(payload.organization_name)

    existing = await db.execute(select(Organization).where(Organization.slug == slug))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An organization with a similar name is already registered.",
        )

    organization = Organization(name=payload.organization_name, slug=slug)
    db.add(organization)
    await db.commit()
    await db.refresh(organization)

    try:
        user = await admin_create_user(
            email=payload.email,
            password=payload.password,
            email_confirm=True,
            organization_id=organization.id,
            app_role="admin",
            user_metadata={"full_name": payload.full_name},
        )
    except SupabaseOperationError as exc:
        # Roll back the organization so a retry doesn't collide on the slug.
        await db.delete(organization)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create your account. The email may already be registered.",
        ) from exc

    return RegisterResponse(
        user_id=user["id"],
        email=user["email"],
        organization_id=str(organization.id),
        organization_name=organization.name,
    )