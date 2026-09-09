from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.crud.incident import (
    create_incident,
    delete_incident,
    get_incident,
    get_incidents,
    update_incident,
)
from app.schemas.incident import (
    IncidentCreate,
    IncidentResponse,
    IncidentUpdate,
)


router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"],
)


@router.post(
    "/",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_incident(
    incident_data: IncidentCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new incident."""
    return await create_incident(
        db=db,
        incident_data=incident_data,
    )


@router.get(
    "/",
    response_model=List[IncidentResponse],
)
async def get_all_incidents(
    db: AsyncSession = Depends(get_db),
):
    """Return all incidents."""
    return await get_incidents(db=db)


@router.get(
    "/{incident_id}",
    response_model=IncidentResponse,
)
async def get_single_incident(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Return a single incident."""
    incident = await get_incident(
        db=db,
        incident_id=incident_id,
    )

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )

    return incident


@router.put(
    "/{incident_id}",
    response_model=IncidentResponse,
)
async def update_existing_incident(
    incident_id: UUID,
    incident_data: IncidentUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing incident."""
    incident = await get_incident(
        db=db,
        incident_id=incident_id,
    )

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )

    return await update_incident(
        db=db,
        incident=incident,
        incident_data=incident_data,
    )


@router.delete(
    "/{incident_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_existing_incident(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete an existing incident."""
    incident = await get_incident(
        db=db,
        incident_id=incident_id,
    )

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )

    await delete_incident(
        db=db,
        incident=incident,
    )