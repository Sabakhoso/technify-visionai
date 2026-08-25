"""
app/core/security.py

Security primitives for the Technify VisionAI backend:

1. Password hashing        -> for locally-managed credentials (service
                               accounts, `scripts/create_admin.py`, any
                               non-Supabase auth path).
2. Internal JWT signing     -> short-lived service-to-service / edge-gateway
                               tokens signed with our own SECRET_KEY.
3. Supabase Auth validation -> verifies the JWT issued by Supabase GoTrue
                               when the frontend logs a user in, WITHOUT a
                               network round-trip (local HS256 signature
                               check against the Supabase JWT secret).
4. FastAPI dependencies     -> get_current_user / get_current_active_user /
                               require_role(...) / get_optional_user, wired
                               into an HTTPBearer security scheme.

Required packages (add to requirements.txt):
    PyJWT[crypto]>=2.8.0
    passlib[bcrypt]>=1.7.4
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from pydantic import BaseModel, ConfigDict

from app.core.config import settings
from app.core.logging import get_logger, user_id_ctx, organization_id_ctx

logger = get_logger(__name__)

# --------------------------------------------------------------------------
# Password hashing
# --------------------------------------------------------------------------

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def get_password_hash(password: str) -> str:
    """Hash a plaintext password for storage. Never store plaintext passwords."""
    if not password or len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    return _pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Constant-time comparison of a plaintext password against its stored hash."""
    try:
        return _pwd_context.verify(plain_password, hashed_password)
    except Exception:  # malformed hash, empty string, etc.
        logger.warning("password_verify_failed_malformed_hash")
        return False


def needs_rehash(hashed_password: str) -> bool:
    """True if the stored hash was made with outdated parameters and should be re-hashed on next login."""
    return _pwd_context.needs_update(hashed_password)


# --------------------------------------------------------------------------
# Internal service-to-service JWTs (our own SECRET_KEY, separate from Supabase)
# --------------------------------------------------------------------------

class TokenPayload(BaseModel):
    sub: str
    exp: int
    iat: int
    type: str = "access"
    scopes: list[str] = []


def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[dict[str, Any]] = None,
) -> str:
    """
    Issues a short-lived internal JWT (e.g. for the edge AI gateway calling
    back into the platform API, or for CLI/admin scripts). This is separate
    from the Supabase-issued user tokens.
    """
    now = datetime.now(timezone.utc)
    expire = now + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode: dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "type": "access",
        "jti": str(uuid.uuid4()),
    }
    if extra_claims:
        to_encode.update(extra_claims)

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_internal_token(token: str) -> TokenPayload:
    """Decode + validate a token minted by `create_access_token` above."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenPayload(**payload)


# --------------------------------------------------------------------------
# Supabase Auth token validation
# --------------------------------------------------------------------------

class SupabaseUser(BaseModel):
    """
    Lightweight representation of the authenticated principal, built directly
    from the validated Supabase JWT claims — no extra network call needed.

    NOTE: `organization_id` and `role` are read from `app_metadata`, which is
    only writable from the backend (via the Supabase service-role key), never
    by the end user — this is what makes it safe to trust for authorization
    decisions. Set these on the Supabase user's app_metadata when a user is
    created/invited into an organization (see Phase 3 — organizations.py).
    """

    model_config = ConfigDict(populate_by_name=True)

    id: uuid.UUID
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str = "authenticated"
    organization_id: Optional[uuid.UUID] = None
    app_role: str = "viewer"  # e.g. viewer | operator | admin | owner
    is_active: bool = True
    raw_claims: dict[str, Any] = {}


def _decode_supabase_jwt(token: str) -> dict[str, Any]:
    """
    Validates the signature, expiry and audience of a Supabase-issued JWT.

    Supabase (self-hosted GoTrue and hosted projects using the legacy JWT
    secret) signs user session tokens with HS256 using the project's JWT
    secret (Project Settings -> API -> JWT Secret). Projects that have
    migrated to asymmetric (RS256/ECC) signing keys should instead verify
    against the project's JWKS endpoint — see `_decode_supabase_jwt_jwks`
    below; toggle via `settings.SUPABASE_JWT_ALGORITHM`.
    """
    algorithm = getattr(settings, "SUPABASE_JWT_ALGORITHM", "HS256")

    if algorithm == "HS256":
        try:
            return jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated",
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session has expired. Please sign in again.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidAudienceError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token audience.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError as exc:
            logger.warning("supabase_jwt_invalid", extra={"error": str(exc)})
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    return _decode_supabase_jwt_jwks(token)


_jwks_client: Optional[jwt.PyJWKClient] = None


def _get_jwks_client() -> jwt.PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        jwks_url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"
        _jwks_client = jwt.PyJWKClient(jwks_url, cache_keys=True, lifespan=3600)
    return _jwks_client


def _decode_supabase_jwt_jwks(token: str) -> dict[str, Any]:
    """Verifies a Supabase JWT signed with an asymmetric key (RS256/ES256) via JWKS."""
    try:
        client = _get_jwks_client()
        signing_key = client.get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256", "ES256"],
            audience="authenticated",
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired. Please sign in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (jwt.InvalidTokenError, jwt.PyJWKClientError) as exc:
        logger.warning("supabase_jwt_jwks_invalid", extra={"error": str(exc)})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_supabase_token(token: str) -> SupabaseUser:
    """Decodes a Supabase Auth access token and maps its claims onto a SupabaseUser."""
    claims = _decode_supabase_jwt(token)

    user_id = claims.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is missing a subject claim.",
        )

    app_metadata = claims.get("app_metadata") or {}
    user_metadata = claims.get("user_metadata") or {}

    organization_id_raw = app_metadata.get("organization_id")
    try:
        organization_id = uuid.UUID(str(organization_id_raw)) if organization_id_raw else None
    except (ValueError, TypeError):
        organization_id = None

    return SupabaseUser(
        id=uuid.UUID(str(user_id)),
        email=claims.get("email"),
        phone=claims.get("phone"),
        role=claims.get("role", "authenticated"),
        organization_id=organization_id,
        app_role=app_metadata.get("app_role", "viewer"),
        is_active=not bool(app_metadata.get("disabled", False)),
        raw_claims={
            "aal": claims.get("aal"),
            "session_id": claims.get("session_id"),
            "user_metadata": user_metadata,
        },
    )


# --------------------------------------------------------------------------
# FastAPI dependencies
# --------------------------------------------------------------------------

_bearer_scheme = HTTPBearer(auto_error=False, description="Supabase Auth access token")

ROLE_HIERARCHY = {
    "viewer": 0,
    "operator": 1,
    "admin": 2,
    "owner": 3,
}


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
) -> SupabaseUser:
    """
    Primary auth dependency. Extracts the `Authorization: Bearer <token>`
    header, validates it as a Supabase Auth token, and returns the
    authenticated principal.

    Use directly on any route that requires a logged-in user:

        @router.get("/cameras")
        async def list_cameras(current_user: SupabaseUser = Depends(get_current_user)):
            ...

    Phase 3's `app/api/deps.py` builds `get_current_org` and DB-hydrated
    variants on top of this (e.g. joining against `app/models/user.py` for
    org-scoped permission checks); this function intentionally stays
    dependency-free of the DB/model layer so `core/` has no upward imports.
    """
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Provide a Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = verify_supabase_token(credentials.credentials)

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been disabled.",
        )

    # Tag structured logs for the remainder of this request with who's making it.
    user_id_ctx.set(str(user.id))
    if user.organization_id:
        organization_id_ctx.set(str(user.organization_id))

    return user


async def get_current_active_user(
    current_user: SupabaseUser = Depends(get_current_user),
) -> SupabaseUser:
    """Alias kept for readability at call sites; activity is already enforced above."""
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
) -> Optional[SupabaseUser]:
    """For endpoints that behave differently for authenticated vs anonymous callers, but don't require auth."""
    if credentials is None or not credentials.credentials:
        return None
    try:
        return verify_supabase_token(credentials.credentials)
    except HTTPException:
        return None


def require_role(minimum_role: str):
    """
    Dependency factory for role-gated endpoints.

        @router.delete("/cameras/{camera_id}")
        async def delete_camera(
            current_user: SupabaseUser = Depends(require_role("admin")),
        ):
            ...

    Roles are ordered viewer < operator < admin < owner; `minimum_role`
    is the lowest role allowed to call the endpoint.
    """
    if minimum_role not in ROLE_HIERARCHY:
        raise ValueError(f"Unknown role '{minimum_role}'. Valid roles: {list(ROLE_HIERARCHY)}")

    async def _dependency(
        current_user: SupabaseUser = Depends(get_current_user),
    ) -> SupabaseUser:
        if ROLE_HIERARCHY.get(current_user.app_role, -1) < ROLE_HIERARCHY[minimum_role]:
            logger.warning(
                "authorization_denied",
                extra={
                    "user_id": str(current_user.id),
                    "user_role": current_user.app_role,
                    "required_role": minimum_role,
                },
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires '{minimum_role}' role or higher.",
            )
        return current_user

    return _dependency


def require_same_organization(organization_id: uuid.UUID, current_user: SupabaseUser) -> None:
    """
    Raises 403 unless the authenticated user belongs to `organization_id`.
    Call this inside endpoints/services after loading a resource, to enforce
    multi-tenant isolation (e.g. before returning a camera/event/incident).
    """
    if current_user.organization_id != organization_id:
        logger.warning(
            "cross_tenant_access_denied",
            extra={
                "user_id": str(current_user.id),
                "user_org": str(current_user.organization_id),
                "resource_org": str(organization_id),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found.",
        )