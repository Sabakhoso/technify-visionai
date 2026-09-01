from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class Detection(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "detections"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    camera_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cameras.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    object_type: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
    )

    track_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        index=True,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    bbox: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    frame_number: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    event = relationship(
        "Event",
        back_populates="detections",
    )

    camera = relationship(
        "Camera",
        back_populates="detections",
    )

    def __repr__(self) -> str:
        return (
            f"<Detection id={self.id} "
            f"object={self.object_type!r} "
            f"track={self.track_id}>"
        )