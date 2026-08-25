"""
app/integrations/supabase_client.py

Supabase client singletons + thin async wrappers used across the backend.

The official `supabase-py` client is synchronous under the hood (it wraps
`httpx.Client`, not `httpx.AsyncClient`). Since our API is async (FastAPI +
asyncpg via SQLAlchemy for our own DB), every Supabase call in this module
is executed in a worker thread via `asyncio.to_thread` so it never blocks
the event loop. Call sites should always `await` these helpers.

Two clients are exposed, for two different trust levels:

- `get_supabase()`       -> uses the ANON key. Respects Row Level Security.
                             Use for anything that should be scoped to "no
                             special privilege" (rare on the backend, since
                             most backend calls act on behalf of the system).

- `get_supabase_admin()` -> uses the SERVICE ROLE key. Bypasses RLS
                             entirely. This is what the backend uses for
                             almost everything: managing users, writing
                             `app_metadata` (organization_id / app_role —
                             see app/core/security.py), and all Storage
                             operations for evidence clips.

                             NEVER expose the service-role client or key to
                             the frontend. It only ever lives in this
                             process, loaded from settings.SUPABASE_SERVICE_ROLE_KEY.

Required package (add to requirements.txt):
    supabase>=2.4.0
"""

from __future__ import annotations

import asyncio
import uuid
from functools import lru_cache
from typing import Any, Optional

from supabase import Client, create_client
from supabase.lib.client_options import ClientOptions

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


# --------------------------------------------------------------------------
# Client singletons
# --------------------------------------------------------------------------

@lru_cache(maxsize=1)
def get_supabase() -> Client:
    """Anon-key client. Subject to Row Level Security."""
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_ANON_KEY,
        options=ClientOptions(auto_refresh_token=False, persist_session=False),
    )


@lru_cache(maxsize=1)
def get_supabase_admin() -> Client:
    """Service-role client. Bypasses RLS. Backend-only — never expose this key."""
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_ROLE_KEY,
        options=ClientOptions(auto_refresh_token=False, persist_session=False),
    )


class SupabaseOperationError(RuntimeError):
    """Raised when a Supabase Admin API call fails after retries."""


# --------------------------------------------------------------------------
# Internal retry helper
# --------------------------------------------------------------------------

async def _run_with_retries(fn, *, retries: int = 2, op_name: str = "supabase_call"):
    """Runs a sync Supabase SDK call in a worker thread, with basic retry on transient errors."""
    last_exc: Optional[Exception] = None
    for attempt in range(1, retries + 2):
        try:
            return await asyncio.to_thread(fn)
        except Exception as exc:  # noqa: BLE001 - SDK raises varied exception types
            last_exc = exc
            logger.warning(
                "supabase_call_failed",
                extra={"op": op_name, "attempt": attempt, "error": str(exc)},
            )
            if attempt <= retries:
                await asyncio.sleep(0.25 * attempt)
    logger.error("supabase_call_exhausted_retries", extra={"op": op_name, "error": str(last_exc)})
    raise SupabaseOperationError(f"{op_name} failed after {retries + 1} attempts: {last_exc}") from last_exc


# --------------------------------------------------------------------------
# User / auth administration (used by organizations.py, auth.py, create_admin.py)
# --------------------------------------------------------------------------

async def admin_create_user(
    *,
    email: str,
    password: Optional[str] = None,
    email_confirm: bool = True,
    organization_id: Optional[uuid.UUID] = None,
    app_role: str = "viewer",
    user_metadata: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """
    Creates a Supabase Auth user directly (no confirmation email flow),
    tagging it with our authorization claims in `app_metadata` up front.

    Use for admin-provisioned accounts (scripts/create_admin.py, an
    org-admin inviting a teammate with a temp password). For self-serve
    signup, prefer `admin_invite_user_by_email` so the user sets their own
    password via the emailed link.
    """
    admin = get_supabase_admin()
    app_metadata: dict[str, Any] = {"app_role": app_role}
    if organization_id is not None:
        app_metadata["organization_id"] = str(organization_id)

    def _call():
        return admin.auth.admin.create_user(
            {
                "email": email,
                "password": password,
                "email_confirm": email_confirm,
                "app_metadata": app_metadata,
                "user_metadata": user_metadata or {},
            }
        )

    response = await _run_with_retries(_call, op_name="admin_create_user")
    logger.info("supabase_user_created", extra={"email": email, "organization_id": str(organization_id) if organization_id else None})
    return _serialize_user(response.user)


async def admin_invite_user_by_email(
    *,
    email: str,
    organization_id: uuid.UUID,
    app_role: str = "viewer",
    redirect_to: Optional[str] = None,
) -> dict[str, Any]:
    """Sends a Supabase invite email; the user sets their own password on accept."""
    admin = get_supabase_admin()
    app_metadata = {"app_role": app_role, "organization_id": str(organization_id)}

    def _call():
        options: dict[str, Any] = {"data": app_metadata}
        if redirect_to:
            options["redirect_to"] = redirect_to
        return admin.auth.admin.invite_user_by_email(email, options)

    response = await _run_with_retries(_call, op_name="admin_invite_user_by_email")
    logger.info("supabase_user_invited", extra={"email": email, "organization_id": str(organization_id)})
    return _serialize_user(response.user)


async def admin_get_user(user_id: uuid.UUID) -> Optional[dict[str, Any]]:
    admin = get_supabase_admin()

    def _call():
        return admin.auth.admin.get_user_by_id(str(user_id))

    try:
        response = await _run_with_retries(_call, op_name="admin_get_user", retries=1)
    except SupabaseOperationError:
        return None
    return _serialize_user(response.user) if response and response.user else None


async def admin_update_user_app_metadata(
    user_id: uuid.UUID,
    *,
    organization_id: Optional[uuid.UUID] = None,
    app_role: Optional[str] = None,
    disabled: Optional[bool] = None,
) -> dict[str, Any]:
    """
    Updates the authorization claims baked into the user's `app_metadata`.
    This is the ONLY place that should ever change organization_id/app_role
    — it's what `get_current_user` in app/core/security.py trusts.
    """
    admin = get_supabase_admin()
    patch: dict[str, Any] = {}
    if organization_id is not None:
        patch["organization_id"] = str(organization_id)
    if app_role is not None:
        patch["app_role"] = app_role
    if disabled is not None:
        patch["disabled"] = disabled

    def _call():
        return admin.auth.admin.update_user_by_id(str(user_id), {"app_metadata": patch})

    response = await _run_with_retries(_call, op_name="admin_update_user_app_metadata")
    logger.info("supabase_user_metadata_updated", extra={"user_id": str(user_id), "patch": patch})
    return _serialize_user(response.user)


async def admin_delete_user(user_id: uuid.UUID) -> None:
    admin = get_supabase_admin()

    def _call():
        return admin.auth.admin.delete_user(str(user_id))

    await _run_with_retries(_call, op_name="admin_delete_user")
    logger.info("supabase_user_deleted", extra={"user_id": str(user_id)})


async def admin_list_users(*, page: int = 1, per_page: int = 100) -> list[dict[str, Any]]:
    admin = get_supabase_admin()

    def _call():
        return admin.auth.admin.list_users(page=page, per_page=per_page)

    response = await _run_with_retries(_call, op_name="admin_list_users")
    users = response.users if hasattr(response, "users") else response
    return [_serialize_user(u) for u in users]


def _serialize_user(user: Any) -> dict[str, Any]:
    if user is None:
        return {}
    return {
        "id": user.id,
        "email": getattr(user, "email", None),
        "phone": getattr(user, "phone", None),
        "app_metadata": getattr(user, "app_metadata", {}) or {},
        "user_metadata": getattr(user, "user_metadata", {}) or {},
        "created_at": str(getattr(user, "created_at", "")),
        "last_sign_in_at": str(getattr(user, "last_sign_in_at", "") or ""),
        "confirmed_at": str(getattr(user, "confirmed_at", "") or ""),
    }