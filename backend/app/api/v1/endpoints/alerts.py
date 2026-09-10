"""
Technify VisionAI — Alerts API

Endpoints for creating, listing, viewing, updating, and deleting alerts.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.alert import (
    create_alert,
    delete_alert,
    get_alert,
    get_alerts,
    update_alert,
)
from app.schemas.alert import (
    AlertCreate,
    AlertResponse,
    AlertUpdate,
)


router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"],
)


@router.post(
    "/",
    response_model=AlertResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_alert(
    alert_data: AlertCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new alert."""
    return await create_alert(
        db=db,
        alert_data=alert_data,
    )


@router.get(
    "/",
    response_model=List[AlertResponse],
)
async def list_alerts(
    db: AsyncSession = Depends(get_db),
):
    """Return all alerts, newest first."""
    return await get_alerts(db=db)


@router.get(
    "/{alert_id}",
    response_model=AlertResponse,
)
async def get_single_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Return a single alert by ID."""
    alert = await get_alert(
        db=db,
        alert_id=alert_id,
    )

    if alert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found.",
        )

    return alert


@router.put(
    "/{alert_id}",
    response_model=AlertResponse,
)
async def update_existing_alert(
    alert_id: UUID,
    alert_data: AlertUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing alert."""
    alert = await get_alert(
        db=db,
        alert_id=alert_id,
    )

    if alert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found.",
        )

    return await update_alert(
        db=db,
        alert=alert,
        alert_data=alert_data,
    )


@router.delete(
    "/{alert_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_existing_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete an existing alert."""
    alert = await get_alert(
        db=db,
        alert_id=alert_id,
    )

    if alert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found.",
        )

    await delete_alert(
        db=db,
        alert=alert,
    )