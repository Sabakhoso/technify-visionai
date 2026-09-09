from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RuleCreate(BaseModel):
    organization_id: UUID
    camera_id: UUID
    zone_id: Optional[UUID] = None

    name: str = Field(min_length=1, max_length=255)
    rule_type: str = Field(min_length=1, max_length=40)

    object_types: list[str] = Field(default_factory=list)

    severity: str = Field(
        default="medium",
        min_length=1,
        max_length=20,
    )

    min_duration_seconds: Optional[int] = Field(
        default=None,
        ge=0,
    )

    schedule: Optional[dict] = None

    actions: list[str] = Field(default_factory=list)

    config: dict = Field(default_factory=dict)

    is_active: bool = True


class RuleUpdate(BaseModel):
    camera_id: Optional[UUID] = None
    zone_id: Optional[UUID] = None

    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    rule_type: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=40,
    )

    object_types: Optional[list[str]] = None

    severity: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=20,
    )

    min_duration_seconds: Optional[int] = Field(
        default=None,
        ge=0,
    )

    schedule: Optional[dict] = None
    actions: Optional[list[str]] = None
    config: Optional[dict] = None
    is_active: Optional[bool] = None


class RuleResponse(BaseModel):
    id: UUID
    organization_id: UUID
    camera_id: UUID
    zone_id: Optional[UUID] = None

    name: str
    rule_type: str
    object_types: list[str]

    severity: str
    min_duration_seconds: Optional[int] = None

    schedule: Optional[dict] = None
    actions: list[str]
    config: dict

    is_active: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)