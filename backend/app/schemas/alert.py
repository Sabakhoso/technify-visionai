
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AlertCreate(BaseModel):
    organization_id: UUID

    event_id: Optional[UUID] = None

    incident_id: Optional[UUID] = None

    user_id: Optional[UUID] = None

    channel: str = Field(
        min_length=1,
        max_length=20,
    )

    destination: str = Field(
        min_length=1,
        max_length=320,
    )

    status: str = Field(
        default="pending",
        min_length=1,
        max_length=20,
    )

    provider: Optional[str] = Field(
        default=None,
        max_length=40,
    )


class AlertUpdate(BaseModel):
    status: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=20,
    )

    provider: Optional[str] = Field(
        default=None,
        max_length=40,
    )

    provider_message_id: Optional[str] = Field(
        default=None,
        max_length=255,
    )

    error: Optional[str] = None

    sent_at: Optional[datetime] = None

    is_read: Optional[bool] = None


class AlertResponse(BaseModel):
    id: UUID

    organization_id: UUID

    event_id: Optional[UUID] = None

    incident_id: Optional[UUID] = None

    user_id: Optional[UUID] = None

    channel: str

    destination: str

    status: str

    is_read: bool

    provider: Optional[str] = None

    provider_message_id: Optional[str] = None

    error: Optional[str] = None

    sent_at: Optional[datetime] = None

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class DashboardNotificationResponse(BaseModel):
    id: UUID

    event_id: Optional[UUID] = None

    camera_id: UUID

    camera_name: str

    event_type: str

    severity: str

    description: Optional[str] = None

    status: str

    is_read: bool

    created_at: datetime

