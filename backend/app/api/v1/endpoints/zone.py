from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.crud.zone import (
    create_zone,
    get_zone as get_zone_from_db,
    get_zones,
    update_zone,
    delete_zone,
)
from app.schemas.zone import (
    ZoneCreate,
    ZoneResponse,
    ZoneUpdate,
)


router = APIRouter(
    tags=["Zones"],
)


@router.post(
    "/",
    response_model=ZoneResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_zone(
    zone_data: ZoneCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new monitoring zone."""

    zone = await create_zone(
        db=db,
        zone_data=zone_data,
    )

    return zone


@router.get(
    "/",
    response_model=List[ZoneResponse],
)
async def get_all_zones(
    db: AsyncSession = Depends(get_db),
):
    """Return all monitoring zones."""

    zones = await get_zones(db=db)

    return zones


@router.get(
    "/{zone_id}",
    response_model=ZoneResponse,
)
async def get_single_zone(
    zone_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Return a single monitoring zone."""

    zone = await get_zone_from_db(
        db=db,
        zone_id=zone_id,
    )

    if zone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zone not found",
        )

    return zone


@router.put(
    "/{zone_id}",
    response_model=ZoneResponse,
)
async def update_existing_zone(
    zone_id: str,
    zone_data: ZoneUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing monitoring zone."""

    zone = await get_zone_from_db(
        db=db,
        zone_id=zone_id,
    )

    if zone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zone not found",
        )

    updated_zone = await update_zone(
        db=db,
        zone=zone,
        zone_data=zone_data,
    )

    return updated_zone


@router.delete(
    "/{zone_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_existing_zone(
    zone_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete an existing monitoring zone."""

    zone = await get_zone_from_db(
        db=db,
        zone_id=zone_id,
    )

    if zone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zone not found",
        )

    await delete_zone(
        db=db,
        zone=zone,
    )