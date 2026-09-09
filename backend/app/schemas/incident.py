from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class IncidentCreate(BaseModel):
    organization_id: UUID

    title: str = Field(
        min_length=1,
        max_length=255,
    )

    status: str = Field(
        default="open",
        min_length=1,
        max_length=20,
    )

    severity: str = Field(
        default="medium",
        min_length=1,
        max_length=20,
    )

    summary: Optional[str] = None
    assigned_to: Optional[UUID] = None


class IncidentUpdate(BaseModel):
    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    status: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=20,
    )

    severity: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=20,
    )

    summary: Optional[str] = None
    assigned_to: Optional[UUID] = None

    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


class IncidentResponse(BaseModel):
    id: UUID
    organization_id: UUID
    title: str
    status: str
    severity: str
    summary: Optional[str] = None
    assigned_to: Optional[UUID] = None

    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)