from typing import List
from uuid import UUID

from app.services.rtsp_health import check_rtsp_stream
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.crud.camera import (
    create_camera,
    delete_camera,
    get_camera as get_camera_from_db,
    update_camera,
)
from app.models.camera import Camera
from app.schemas.camera import (
    CameraCreate,
    CameraResponse,
    CameraUpdate,
)
from app.services.camera_health import (
    mark_camera_offline,
    mark_camera_online,
)


router = APIRouter(
    prefix="/cameras",
    tags=["Cameras"],
)


@router.post(
    "/",
    response_model=CameraResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_camera(
    camera_data: CameraCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new camera."""
    camera = await create_camera(
        db=db,
        camera_data=camera_data,
    )

    return camera


@router.get(
    "/",
    response_model=List[dict],
)
async def get_cameras(
    db: AsyncSession = Depends(get_db),
):
    """Return all cameras."""
    result = await db.execute(
        select(Camera).order_by(Camera.created_at.desc())
    )

    cameras = result.scalars().all()

    return [
        {
            "id": str(camera.id),
            "name": camera.name,
            "status": camera.status,
        }
        for camera in cameras
    ]


@router.get(
    "/{camera_id}",
    response_model=dict,
)
async def get_camera(
    camera_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Return a single camera by ID."""
    camera = await get_camera_from_db(
        db=db,
        camera_id=camera_id,
    )

    if camera is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found",
        )

    return {
        "id": str(camera.id),
        "name": camera.name,
        "status": camera.status,
    }


@router.put(
    "/{camera_id}",
    response_model=CameraResponse,
)
async def update_existing_camera(
    camera_id: UUID,
    camera_data: CameraUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing camera."""
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
    """Delete an existing camera."""
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
    """
    Mark a camera as online and update last_seen_at.

    This endpoint is currently manual and will later be
    called by the real RTSP/OpenCV health checker.
    """
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
    """
    Mark a camera as offline.

    This endpoint is currently manual and will later be
    triggered when the RTSP/OpenCV health checker cannot
    connect to the camera.
    """
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
    """
    Check the camera's RTSP stream and update its health status.
    """
    camera = await get_camera_from_db(
        db=db,
        camera_id=camera_id,
    )

    if camera is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found",
        )

    # Camera has no RTSP URL.
    if not camera.rtsp_url:
        return await mark_camera_offline(
            db=db,
            camera=camera,
        )

    # Check whether the RTSP stream is reachable
    # and a video frame can be read.
    stream_available = check_rtsp_stream(
        rtsp_url=camera.rtsp_url,
    )

    if stream_available:
        return await mark_camera_online(
            db=db,
            camera=camera,
        )

    return await mark_camera_offline(
        db=db,
        camera=camera,
    )