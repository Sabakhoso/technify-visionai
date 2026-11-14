"""
app/models/base.py

Shared SQLAlchemy mixins that every ORM model in Technify VisionAI reuses.
Compatible with PostgreSQL (Supabase) and SQLite (Local development).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, func, Uuid
from sqlalchemy.orm import Mapped, mapped_column


def _utc_now():
    return datetime.now(timezone.utc)


class UUIDMixin:
    """Adds a UUID primary key."""

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


class TimestampMixin:
    """Adds created_at / updated_at audit columns."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=_utc_now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=_utc_now,
        onupdate=_utc_now,
    )
