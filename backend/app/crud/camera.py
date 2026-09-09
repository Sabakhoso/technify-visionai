from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.camera import Camera
from app.schemas.camera import CameraCreate, CameraUpdate


async def create_camera(
    db: AsyncSession,
    camera_data: CameraCreate,
) -> Camera:
    camera = Camera(**camera_data.model_dump())

    db.add(camera)
    await db.commit()
    await db.refresh(camera)

    return camera


async def get_camera(
    db: AsyncSession,
    camera_id: UUID,
) -> Camera | None:
    result = await db.execute(
        select(Camera).where(Camera.id == camera_id)
    )

    return result.scalar_one_or_none()


async def get_cameras(
    db: AsyncSession,
) -> list[Camera]:
    result = await db.execute(
        select(Camera).order_by(Camera.created_at.desc())
    )

    return list(result.scalars().all())


async def update_camera(
    db: AsyncSession,
    camera: Camera,
    camera_data: CameraUpdate,
) -> Camera:
    update_data = camera_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(camera, field, value)

    await db.commit()
    await db.refresh(camera)

    return camera


async def delete_camera(
    db: AsyncSession,
    camera: Camera,
) -> None:
    await db.delete(camera)
    await db.commit()