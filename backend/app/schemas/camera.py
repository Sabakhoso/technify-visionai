from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CameraCreate(BaseModel):
    organization_id: UUID
    name: str
    location: Optional[str] = None
    rtsp_url: Optional[str] = None
    status: str = "unknown"
    is_active: bool = True
    fps: Optional[int] = None
    resolution: Optional[str] = None


class CameraUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    rtsp_url: Optional[str] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None
    fps: Optional[int] = None
    resolution: Optional[str] = None


class CameraResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    location: Optional[str] = None
    rtsp_url: Optional[str] = None
    status: str
    is_active: bool
    fps: Optional[int] = None
    resolution: Optional[str] = None
    last_seen_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)