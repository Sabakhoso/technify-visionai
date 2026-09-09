from typing import List

from app.crud.camera import (
    create_camera,
    get_camera as get_camera_from_db,
    update_camera,
    delete_camera,
)
from app.schemas.camera import CameraCreate, CameraResponse, CameraUpdate
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.camera import Camera


router = APIRouter(
    prefix="/cameras",
    tags=["Cameras"],
)

@router.post("/", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
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

@router.get("/", response_model=List[dict])
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
            "status": getattr(camera, "status", None),
        }
        for camera in cameras
    ]


@router.get("/{camera_id}", response_model=dict)
async def get_camera(
    camera_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Return a single camera by ID."""

    result = await db.execute(
        select(Camera).where(Camera.id == camera_id)
    )

    camera = result.scalar_one_or_none()

    if camera is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found",
        )

    return {
        "id": str(camera.id),
        "name": camera.name,
        "status": getattr(camera, "status", None),
    }

@router.put("/{camera_id}", response_model=CameraResponse)
async def update_existing_camera(
    camera_id: str,
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

    updated_camera = await update_camera(
        db=db,
        camera=camera,
        camera_data=camera_data,
    )

    return updated_camera

@router.delete("/{camera_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_camera(
    camera_id: str,
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