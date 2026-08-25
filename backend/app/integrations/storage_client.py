"""
app/integrations/storage_client.py

Evidence storage on top of Supabase Storage: upload/download/sign/delete for
event snapshots, evidence clips and their metadata JSON (see product doc
section 32 — "Evidence clips": snapshot.jpg + clip.mp4 + metadata.json per
event).

Path convention (keeps every tenant's evidence logically isolated even
though Storage itself doesn't enforce it — enforce access via RLS storage
policies on the bucket + our own org-scoped signed URLs):

    {organization_id}/{camera_id}/{event_id}/snapshot.jpg
    {organization_id}/{camera_id}/{event_id}/clip.mp4
    {organization_id}/{camera_id}/{event_id}/metadata.json

Required package: already covered by `supabase` (used in supabase_client.py).
"""

from __future__ import annotations

import asyncio
import json
import mimetypes
import uuid
from dataclasses import dataclass
from typing import Any, Optional

from app.core.config import settings
from app.core.logging import get_logger
from app.integrations.supabase_client import get_supabase_admin, _run_with_retries, SupabaseOperationError

logger = get_logger(__name__)

# Configure in app/core/config.py: SUPABASE_EVIDENCE_BUCKET (default below is
# used if the setting isn't present, to avoid breaking earlier phases).
EVIDENCE_BUCKET = getattr(settings, "SUPABASE_EVIDENCE_BUCKET", "evidence")

_ALLOWED_CONTENT_TYPES = {
    "image/jpeg", "image/png", "video/mp4", "application/json",
}

# Signed URLs used for evidence access should be short-lived — evidence is
# sensitive (see product doc section 33 — Privacy-by-design / audit logs).
DEFAULT_SIGNED_URL_EXPIRY_SECONDS = 300  # 5 minutes


@dataclass
class EvidenceObject:
    path: str
    bucket: str
    content_type: str
    size_bytes: int


def _object_path(organization_id: uuid.UUID, camera_id: uuid.UUID, event_id: uuid.UUID, filename: str) -> str:
    return f"{organization_id}/{camera_id}/{event_id}/{filename}"


async def ensure_bucket_exists() -> None:
    """
    Idempotently ensures the evidence bucket exists (private, not public —
    all access must go through short-lived signed URLs). Safe to call at
    startup; swallows the "already exists" case.
    """
    admin = get_supabase_admin()

    def _list():
        return admin.storage.list_buckets()

    def _create():
        return admin.storage.create_bucket(
            EVIDENCE_BUCKET,
            options={"public": False, "file_size_limit": "104857600"},  # 100 MB/object ceiling
        )

    try:
        buckets = await _run_with_retries(_list, op_name="storage_list_buckets", retries=1)
        existing_names = {getattr(b, "name", None) or b.get("name") for b in buckets}
        if EVIDENCE_BUCKET not in existing_names:
            await _run_with_retries(_create, op_name="storage_create_bucket", retries=1)
            logger.info("storage_bucket_created", extra={"bucket": EVIDENCE_BUCKET})
    except SupabaseOperationError as exc:
        # Non-fatal at startup — log loudly so it's caught before it becomes
        # a 500 on the first evidence upload.
        logger.error("storage_bucket_ensure_failed", extra={"bucket": EVIDENCE_BUCKET, "error": str(exc)})


async def upload_bytes(
    *,
    organization_id: uuid.UUID,
    camera_id: uuid.UUID,
    event_id: uuid.UUID,
    filename: str,
    content: bytes,
    content_type: Optional[str] = None,
    upsert: bool = True,
) -> EvidenceObject:
    """Low-level upload used by the more specific helpers below."""
    resolved_content_type = content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
    if resolved_content_type not in _ALLOWED_CONTENT_TYPES:
        logger.warning(
            "storage_upload_unexpected_content_type",
            extra={"filename": filename, "content_type": resolved_content_type},
        )

    path = _object_path(organization_id, camera_id, event_id, filename)
    admin = get_supabase_admin()

    def _call():
        return admin.storage.from_(EVIDENCE_BUCKET).upload(
            path=path,
            file=content,
            file_options={
                "content-type": resolved_content_type,
                "upsert": "true" if upsert else "false",
                "cache-control": "3600",
            },
        )

    await _run_with_retries(_call, op_name="storage_upload")
    logger.info(
        "evidence_uploaded",
        extra={
            "organization_id": str(organization_id),
            "camera_id": str(camera_id),
            "event_id": str(event_id),
            "filename": filename,
            "size_bytes": len(content),
        },
    )
    return EvidenceObject(
        path=path,
        bucket=EVIDENCE_BUCKET,
        content_type=resolved_content_type,
        size_bytes=len(content),
    )


async def upload_snapshot(
    *, organization_id: uuid.UUID, camera_id: uuid.UUID, event_id: uuid.UUID, image_bytes: bytes
) -> EvidenceObject:
    return await upload_bytes(
        organization_id=organization_id,
        camera_id=camera_id,
        event_id=event_id,
        filename="snapshot.jpg",
        content=image_bytes,
        content_type="image/jpeg",
    )


async def upload_evidence_clip(
    *, organization_id: uuid.UUID, camera_id: uuid.UUID, event_id: uuid.UUID, clip_bytes: bytes
) -> EvidenceObject:
    """
    Uploads the pre/post-buffer evidence clip for an event (see product doc
    section 32 — typically a 15-30s mp4 assembled by the edge gateway before
    this is called).
    """
    return await upload_bytes(
        organization_id=organization_id,
        camera_id=camera_id,
        event_id=event_id,
        filename="clip.mp4",
        content=clip_bytes,
        content_type="video/mp4",
    )


async def upload_event_metadata(
    *, organization_id: uuid.UUID, camera_id: uuid.UUID, event_id: uuid.UUID, metadata: dict[str, Any]
) -> EvidenceObject:
    payload = json.dumps(metadata, default=str, indent=2).encode("utf-8")
    return await upload_bytes(
        organization_id=organization_id,
        camera_id=camera_id,
        event_id=event_id,
        filename="metadata.json",
        content=payload,
        content_type="application/json",
    )


async def get_signed_url(
    *,
    organization_id: uuid.UUID,
    camera_id: uuid.UUID,
    event_id: uuid.UUID,
    filename: str,
    expires_in: int = DEFAULT_SIGNED_URL_EXPIRY_SECONDS,
) -> str:
    """
    Generates a short-lived signed URL for the frontend to fetch/display
    evidence. Callers MUST authorize the request (org membership + role —
    see `require_same_organization` in app/core/security.py) BEFORE calling
    this; this function does not itself check permissions.
    """
    path = _object_path(organization_id, camera_id, event_id, filename)
    admin = get_supabase_admin()

    def _call():
        return admin.storage.from_(EVIDENCE_BUCKET).create_signed_url(path, expires_in)

    result = await _run_with_retries(_call, op_name="storage_signed_url")
    signed_url = result.get("signedURL") or result.get("signed_url")
    if not signed_url:
        raise SupabaseOperationError(f"No signed URL returned for {path}")
    return signed_url


async def download_bytes(
    *, organization_id: uuid.UUID, camera_id: uuid.UUID, event_id: uuid.UUID, filename: str
) -> bytes:
    """Server-side download (e.g. for AI re-processing, report generation)."""
    path = _object_path(organization_id, camera_id, event_id, filename)
    admin = get_supabase_admin()

    def _call():
        return admin.storage.from_(EVIDENCE_BUCKET).download(path)

    return await _run_with_retries(_call, op_name="storage_download")


async def delete_event_evidence(
    *, organization_id: uuid.UUID, camera_id: uuid.UUID, event_id: uuid.UUID
) -> None:
    """
    Deletes all evidence objects for a single event (snapshot, clip,
    metadata). Used by retention-policy jobs (see product doc section 33 —
    configurable retention) and by incident deletion flows.
    """
    admin = get_supabase_admin()
    base = f"{organization_id}/{camera_id}/{event_id}"
    paths = [f"{base}/snapshot.jpg", f"{base}/clip.mp4", f"{base}/metadata.json"]

    def _call():
        return admin.storage.from_(EVIDENCE_BUCKET).remove(paths)

    await _run_with_retries(_call, op_name="storage_delete", retries=1)
    logger.info(
        "evidence_deleted",
        extra={"organization_id": str(organization_id), "camera_id": str(camera_id), "event_id": str(event_id)},
    )


async def list_evidence_for_camera(*, organization_id: uuid.UUID, camera_id: uuid.UUID) -> list[dict[str, Any]]:
    """Lists all event evidence folders for a camera — used by retention sweeps and admin review."""
    admin = get_supabase_admin()
    prefix = f"{organization_id}/{camera_id}"

    def _call():
        return admin.storage.from_(EVIDENCE_BUCKET).list(prefix)

    return await _run_with_retries(_call, op_name="storage_list")