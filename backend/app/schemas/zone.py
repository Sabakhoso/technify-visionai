from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ZoneCreate(BaseModel):
    organization_id: UUID
    camera_id: UUID
    name: str
    kind: str = "polygon"
    geometry: list
    direction: Optional[str] = None
    is_active: bool = True


class ZoneUpdate(BaseModel):
    name: Optional[str] = None
    kind: Optional[str] = None
    geometry: Optional[list] = None
    direction: Optional[str] = None
    is_active: Optional[bool] = None


class ZoneResponse(BaseModel):
    id: UUID
    organization_id: UUID
    camera_id: UUID
    name: str
    kind: str
    geometry: list
    direction: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)