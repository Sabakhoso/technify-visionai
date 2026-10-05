
"""
Technify VisionAI — Alerts API

Endpoints for creating, listing, viewing, updating, and deleting alerts.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    SupabaseUser,
    get_current_user,
)
from app.crud.alert import (
    create_alert,
    delete_alert,
    get_alert,
    get_alerts,
    update_alert,
    get_dashboard_notifications,
    get_unread_dashboard_notifications,
)
from app.schemas.alert import (
    AlertCreate,
    AlertResponse,
    AlertUpdate,
    DashboardNotificationResponse,
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
    current_user: SupabaseUser = Depends(get_current_user),
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
    current_user: SupabaseUser = Depends(get_current_user),
):
    """Return all alerts, newest first."""
    return await get_alerts(db=db)


@router.get(
    "/notifications",
    response_model=List[DashboardNotificationResponse],
)
async def list_dashboard_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: SupabaseUser = Depends(get_current_user),
):
    """Return notifications for the dashboard bell."""
    if current_user.organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not assigned to an organization.",
        )

    notifications = await get_dashboard_notifications(
        db=db,
        organization_id=current_user.organization_id,
    )

    return [
        DashboardNotificationResponse(
            id=alert.id,
            event_id=alert.event_id,
            camera_id=camera.id,
            camera_name=camera.name,
            event_type=event.event_type,
            severity=event.severity,
            description=event.description,
            status=alert.status,
            is_read=alert.is_read,
            created_at=alert.created_at,
        )
        for alert, event, camera in notifications
    ]


@router.get(
    "/notifications/unread",
    response_model=List[DashboardNotificationResponse],
)
async def list_unread_dashboard_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: SupabaseUser = Depends(get_current_user),
):
    """Return unread notifications for the dashboard bell."""
    if current_user.organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not assigned to an organization.",
        )

    notifications = await get_unread_dashboard_notifications(
        db=db,
        organization_id=current_user.organization_id,
    )

    return [
        DashboardNotificationResponse(
            id=alert.id,
            event_id=alert.event_id,
            camera_id=camera.id,
            camera_name=camera.name,
            event_type=event.event_type,
            severity=event.severity,
            description=event.description,
            status=alert.status,
            is_read=alert.is_read,
            created_at=alert.created_at,
        )
        for alert, event, camera in notifications
    ]


@router.get(
    "/{alert_id}",
    response_model=AlertResponse,
)
async def get_single_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: SupabaseUser = Depends(get_current_user),
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
    current_user: SupabaseUser = Depends(get_current_user),
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
    current_user: SupabaseUser = Depends(get_current_user),
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

