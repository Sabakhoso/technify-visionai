from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.incident import Incident


router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"],
)


@router.get("/", response_model=List[dict])
async def get_incidents(
    db: AsyncSession = Depends(get_db),
):
    """Return all incidents."""

    result = await db.execute(
        select(Incident)
    )

    incidents = result.scalars().all()

    return [
        {
            "id": str(incident.id),
            "status": getattr(incident, "status", None),
            "severity": getattr(incident, "severity", None),
            "description": getattr(incident, "description", None),
        }
        for incident in incidents
    ]


@router.get("/{incident_id}", response_model=dict)
async def get_incident(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Return a single incident."""

    result = await db.execute(
        select(Incident).where(Incident.id == incident_id)
    )

    incident = result.scalar_one_or_none()

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )

    return {
        "id": str(incident.id),
        "status": getattr(incident, "status", None),
        "severity": getattr(incident, "severity", None),
        "description": getattr(incident, "description", None),
    }