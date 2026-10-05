from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.rtsp_health import check_rtsp_stream
from app.services.ai_camera_manager import (
    start_camera_ai,
    stop_camera_ai,
    is_camera_ai_running,
)

from app.api.deps import get_db
from app.crud.camera import (
    create_camera,
    delete_camera,
    get_camera as get_camera_from_db,
    get_cameras,
    update_camera,
)
from app.models.organization import Organization
from app.schemas.camera import CameraCreate, CameraResponse, CameraUpdate
from app.services.camera_health import mark_camera_offline, mark_camera_online


router = APIRouter(prefix="/cameras", tags=["Cameras"])


async def _default_organization_id(db: AsyncSession) -> UUID:
    """
    No login flow right now, so there's no user to infer an organization
    from. Falls back to the first organization in the DB, creating one
    if the table is empty — just enough to keep camera creation working.
    """
    result = await db.execute(
        select(Organization)
        .order_by(Organization.created_at.asc())
        .limit(1)
    )
    organization = result.scalar_one_or_none()

    if organization is not None:
        return organization.id

    organization = Organization(
        name="Default Organization",
        slug="default-organization",
    )
    db.add(organization)
    await db.commit()
    await db.refresh(organization)

    return organization.id


@router.post(
    "/",
    response_model=CameraResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_camera(
    camera_data: CameraCreate,
    db: AsyncSession = Depends(get_db),
):
    if camera_data.organization_id is None:
        camera_data.organization_id = await _default_organization_id(db)

    return await create_camera(
        db=db,
        camera_data=camera_data,
    )


@router.get(
    "/",
    response_model=List[CameraResponse],
)
async def get_all_cameras(
    db: AsyncSession = Depends(get_db),
):
    return await get_cameras(db)


@router.get(
    "/{camera_id}",
    response_model=CameraResponse,
)
async def get_camera(
    camera_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    camera = await get_camera_from_db(
        db=db,
        camera_id=camera_id,
    )

    if camera is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found",
        )

    return camera


@router.put(
    "/{camera_id}",
    response_model=CameraResponse,
)
async def update_existing_camera(
    camera_id: UUID,
    camera_data: CameraUpdate,
    db: AsyncSession = Depends(get_db),
):
    camera = await get_camera_from_db(
        db=db,
        camera_id=camera_id,
    )

    if camera is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found",
        )

    return await update_camera(
        db=db,
        camera=camera,
        camera_data=camera_data,
    )


@router.delete(
    "/{camera_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_existing_camera(
    camera_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    camera = await get_camera_from_db(
        db=db,
        camera_id=camera_id,
    )

    if camera is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found",
        )

    await delete_camera(
        db=db,
        camera=camera,
    )


@router.post(
    "/{camera_id}/health/online",
    response_model=CameraResponse,
)
async def mark_camera_as_online(
    camera_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    camera = await get_camera_from_db(
        db=db,
        camera_id=camera_id,
    )

    if camera is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found",
        )

    return await mark_camera_online(
        db=db,
        camera=camera,
    )


@router.post(
    "/{camera_id}/health/offline",
    response_model=CameraResponse,
)
async def mark_camera_as_offline(
    camera_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    camera = await get_camera_from_db(
        db=db,
        camera_id=camera_id,
    )

    if camera is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found",
        )

    return await mark_camera_offline(
        db=db,
        camera=camera,
    )


@router.post(
    "/{camera_id}/health/check",
    response_model=CameraResponse,
)
async def check_camera_health(
    camera_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    camera = await get_camera_from_db(
        db=db,
        camera_id=camera_id,
    )

    if camera is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found",
        )

    if not camera.rtsp_url:
        return await mark_camera_offline(
            db=db,
            camera=camera,
        )

    if check_rtsp_stream(camera.rtsp_url):
        return await mark_camera_online(
            db=db,
            camera=camera,
        )

    return await mark_camera_offline(
        db=db,
        camera=camera,
    )


@router.post("/{camera_id}/ai/start")
async def start_camera_ai_processing(
    camera_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    camera = await get_camera_from_db(
        db=db,
        camera_id=camera_id,
    )

    if camera is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found",
        )

    if not camera.rtsp_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Camera has no RTSP URL",
        )

    await start_camera_ai(camera_id)

    return {
        "camera_id": str(camera_id),
        "ai_processing": "started",
    }


@router.post("/{camera_id}/ai/stop")
async def stop_camera_ai_processing(
    camera_id: UUID,
):
    await stop_camera_ai(camera_id)

    return {
        "camera_id": str(camera_id),
        "ai_processing": "stopped",
    }


@router.get("/{camera_id}/ai/status")
async def get_camera_ai_status(
    camera_id: UUID,
):
    return {
        "camera_id": str(camera_id),
        "ai_processing": is_camera_ai_running(camera_id),
    }