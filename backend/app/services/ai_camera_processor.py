from datetime import datetime, timezone
from uuid import UUID

from app.crud.camera import get_camera
from app.crud.event import create_event
from app.schemas.event import EventCreate
from app.services.event_engine import create_event as create_ai_event
from app.services.vision_pipeline import process_camera_stream


async def process_camera(
    camera_id: UUID,
) -> None:
    """
    Process one camera stream and create events
    from AI detections.
    """

    from app.core.database import get_db_context

    async with get_db_context() as db:
        camera = await get_camera(
            db=db,
            camera_id=camera_id,
        )

        if camera is None:
            raise ValueError(
                f"Camera not found: {camera_id}"
            )

        if not camera.rtsp_url:
            raise ValueError(
                f"Camera has no RTSP URL: {camera_id}"
            )

        for detections in process_camera_stream(
            camera.rtsp_url
        ):
            for detection in detections:
                event_data = create_ai_event(
                    detection
                )

                if event_data is None:
                    continue

                event = EventCreate(
                    organization_id=camera.organization_id,
                    camera_id=camera.id,
                    event_type=event_data["event_type"],
                    severity=event_data["severity"],
                    confidence=event_data["confidence"],
                    start_time=datetime.now(timezone.utc),
                    status="new",
                    description=event_data["description"],
                )

                await create_event(
                    db=db,
                    event_data=event,
                )