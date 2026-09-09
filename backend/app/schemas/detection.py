from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DetectionCreate(BaseModel):
    organization_id: UUID
    event_id: Optional[UUID] = None
    camera_id: UUID

    object_type: str
    track_id: Optional[int] = None

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    bbox: dict

    frame_number: Optional[int] = None
    detected_at: datetime


class DetectionResponse(BaseModel):
    id: UUID
    organization_id: UUID
    event_id: Optional[UUID] = None
    camera_id: UUID

    object_type: str
    track_id: Optional[int] = None
    confidence: float

    bbox: dict

    frame_number: Optional[int] = None
    detected_at: datetime

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)