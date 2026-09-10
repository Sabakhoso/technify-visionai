import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.camera import Camera
from app.services.camera_health import (
    mark_camera_offline,
    mark_camera_online,
)
from app.services.rtsp_health import check_rtsp_stream


async def check_all_cameras(
    db: AsyncSession,
) -> None:
    """
    Check all active cameras and update their health status.
    """
    result = await db.execute(
        select(Camera).where(
            Camera.is_active.is_(True)
        )
    )

    cameras = result.scalars().all()

    for camera in cameras:
        if not camera.rtsp_url:
            await mark_camera_offline(
                db=db,
                camera=camera,
            )
            continue

        stream_available = await asyncio.to_thread(
            check_rtsp_stream,
            camera.rtsp_url,
        )

        if stream_available:
            await mark_camera_online(
                db=db,
                camera=camera,
            )
        else:
            await mark_camera_offline(
                db=db,
                camera=camera,
            )