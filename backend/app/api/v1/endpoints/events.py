from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.event import Event


router = APIRouter(
    prefix="/events",
    tags=["Events"],
)


@router.get("/", response_model=List[dict])
async def get_events(
    db: AsyncSession = Depends(get_db),
):
    """Return all security events."""

    result = await db.execute(
        select(Event).order_by(Event.created_at.desc())
    )

    events = result.scalars().all()

    return [
        {
            "id": str(event.id),
            "camera_id": str(event.camera_id) if event.camera_id else None,
            "event_type": getattr(event, "event_type", None),
            "description": getattr(event, "description", None),
            "severity": getattr(event, "severity", None),
        }
        for event in events
    ]


@router.get("/{event_id}", response_model=dict)
async def get_event(
    event_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Return a single event."""

    result = await db.execute(
        select(Event).where(Event.id == event_id)
    )

    event = result.scalar_one_or_none()

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    return {
        "id": str(event.id),
        "camera_id": str(event.camera_id) if event.camera_id else None,
        "event_type": getattr(event, "event_type", None),
        "description": getattr(event, "description", None),
        "severity": getattr(event, "severity", None),
    }