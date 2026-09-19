import asyncio
from uuid import UUID

from app.services.ai_camera_processor import process_camera


# Stores running AI tasks by camera ID
_camera_tasks: dict[UUID, asyncio.Task] = {}


async def start_camera_ai(camera_id: UUID) -> None:
    """
    Start AI processing for a camera.
    """

    if camera_id in _camera_tasks:
        return

    task = asyncio.create_task(
        process_camera(camera_id)
    )

    _camera_tasks[camera_id] = task


async def stop_camera_ai(camera_id: UUID) -> None:
    """
    Stop AI processing for a camera.
    """

    task = _camera_tasks.get(camera_id)

    if task is None:
        return

    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        pass

    _camera_tasks.pop(camera_id, None)


def is_camera_ai_running(camera_id: UUID) -> bool:
    """
    Check whether AI processing is running for a camera.
    """

    return camera_id in _camera_tasks