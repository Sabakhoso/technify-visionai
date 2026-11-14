from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, JSON, String, text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class Rule(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "rules"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    camera_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("cameras.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    zone_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("zones.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    rule_type: Mapped[str] = mapped_column(String(40), nullable=False)
    object_types: Mapped[list] = mapped_column(
        JSON, nullable=False, default=list
    )
    severity: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'medium'"))
    min_duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    schedule: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    actions: Mapped[list] = mapped_column(
        JSON, nullable=False, default=list
    )
    config: Mapped[dict] = mapped_column(
        JSON, nullable=False, default=dict
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))

    def __repr__(self) -> str:
        return f"<Rule id={self.id} type={self.rule_type!r} camera={self.camera_id}>"
