"""
Technify VisionAI — Alerts API

Endpoints for creating, listing, viewing, updating, and deleting alerts.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.alert import Alert


router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"],
)


# --------------------------------------------------------------------------
# List alerts
# --------------------------------------------------------------------------

@router.get("/")
async def list_alerts(
    db: AsyncSession = Depends(get_db),
):
    """Return all alerts."""

    result = await db.execute(
        select(Alert).order_by(Alert.created_at.desc())
    )

    alerts = result.scalars().all()

    return alerts


# --------------------------------------------------------------------------
# Get alert
# --------------------------------------------------------------------------

@router.get("/{alert_id}")
async def get_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Return a single alert by ID."""

    result = await db.execute(
        select(Alert).where(Alert.id == alert_id)
    )

    alert = result.scalar_one_or_none()

    if alert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found.",
        )

    return alert


# --------------------------------------------------------------------------
# Delete alert
# --------------------------------------------------------------------------

@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete an alert by ID."""

    result = await db.execute(
        select(Alert).where(Alert.id == alert_id)
    )

    alert = result.scalar_one_or_none()

    if alert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found.",
        )

    await db.delete(alert)
    await db.commit()

    return {
        "message": "Alert deleted successfully.",
        "alert_id": str(alert_id),
    }