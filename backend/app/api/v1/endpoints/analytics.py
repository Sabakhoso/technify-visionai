"""
Technify VisionAI — Analytics API
"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.camera import Camera
from app.models.event import Event
from app.models.incident import Incident


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get("/summary")
async def analytics_summary(
    db: AsyncSession = Depends(get_db),
):
    """
    Return a basic system analytics summary.
    """

    camera_result = await db.execute(
        select(func.count()).select_from(Camera)
    )
    camera_count = camera_result.scalar_one()

    event_result = await db.execute(
        select(func.count()).select_from(Event)
    )
    event_count = event_result.scalar_one()

    incident_result = await db.execute(
        select(func.count()).select_from(Incident)
    )
    incident_count = incident_result.scalar_one()

    return {
        "cameras": camera_count,
        "events": event_count,
        "incidents": incident_count,
    }


@router.get("/events")
async def event_analytics(
    db: AsyncSession = Depends(get_db),
):
    """
    Return event count for the last 24 hours.
    """

    since = datetime.now(timezone.utc) - timedelta(hours=24)

    result = await db.execute(
        select(func.count())
        .select_from(Event)
        .where(Event.created_at >= since)
    )

    count = result.scalar_one()

    return {
        "period": "last_24_hours",
        "events": count,
    }