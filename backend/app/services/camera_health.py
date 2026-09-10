from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.camera import Camera


ONLINE = "online"
OFFLINE = "offline"
UNKNOWN = "unknown"


async def mark_camera_online(
    db: AsyncSession,
    camera: Camera,
) -> Camera:
    """
    Mark a camera as online and update its last seen time.
    """
    camera.status = ONLINE
    camera.last_seen_at = datetime.now(timezone.utc).replace(tzinfo=None)

    await db.commit()
    await db.refresh(camera)

    return camera


async def mark_camera_offline(
    db: AsyncSession,
    camera: Camera,
) -> Camera:
    """
    Mark a camera as offline.
    """
    camera.status = OFFLINE

    await db.commit()
    await db.refresh(camera)

    return camera


async def get_camera_health(
    db: AsyncSession,
    camera_id: UUID,
) -> Camera | None:
    """
    Get a camera so its current health status can be checked.
    """
    camera = await db.get(Camera, camera_id)

    return camera