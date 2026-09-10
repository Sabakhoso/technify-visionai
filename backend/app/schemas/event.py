from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.event import EventSeverity, EventStatus


class EventCreate(BaseModel):
    organization_id: UUID
    camera_id: UUID
    event_type: str
    severity: EventSeverity = EventSeverity.MEDIUM
    confidence: Optional[float] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    status: EventStatus = EventStatus.NEW
    description: Optional[str] = None


class EventResponse(BaseModel):
    id: UUID
    organization_id: UUID
    incident_id: Optional[UUID] = None
    camera_id: UUID
    event_type: str
    severity: EventSeverity
    confidence: Optional[float] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    status: EventStatus
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)