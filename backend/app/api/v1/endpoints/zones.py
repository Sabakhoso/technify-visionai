from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.zone import Zone


router = APIRouter(
    prefix="/zones",
    tags=["Zones"],
)


@router.get("/", response_model=List[dict])
async def get_zones(
    db: AsyncSession = Depends(get_db),
):
    """Return all monitoring zones."""

    result = await db.execute(
        select(Zone)
    )

    zones = result.scalars().all()

    return [
        {
            "id": str(zone.id),
            "name": getattr(zone, "name", None),
            "description": getattr(zone, "description", None),
        }
        for zone in zones
    ]


@router.get("/{zone_id}", response_model=dict)
async def get_zone(
    zone_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Return a single monitoring zone."""

    result = await db.execute(
        select(Zone).where(Zone.id == zone_id)
    )

    zone = result.scalar_one_or_none()

    if zone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zone not found",
        )

    return {
        "id": str(zone.id),
        "name": getattr(zone, "name", None),
        "description": getattr(zone, "description", None),
    }