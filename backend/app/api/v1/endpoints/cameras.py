import asyncio
import cv2
import logging
import numpy as np
import time
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.crud.camera import (
    create_camera,
    delete_camera,
    get_camera as get_camera_from_db,
    get_cameras,
    update_camera,
)
from app.models.camera import Camera
from app.models.organization import Organization
from app.schemas.camera import CameraCreate, CameraResponse, CameraUpdate
from app.services.ai_camera_manager import (
    is_camera_ai_running,
    start_camera_ai,
    stop_camera_ai,
)
from app.services.camera_health import mark_camera_offline, mark_camera_online
from app.services.camera_service import open_camera_stream, release_camera_stream
from app.services.rtsp_health import check_rtsp_stream

logger = logging.getLogger("technify_visionai.cameras")

router = APIRouter(prefix="/cameras", tags=["Cameras"])


def _enrich_camera(camera: Camera) -> CameraResponse:
    """Enriches camera model with live stream URL."""
    resp = CameraResponse.model_validate(camera)
    resp.stream_url = f"http://localhost:8000/api/v1/cameras/{camera.id}/stream"
    return resp


async def _default_organization_id(db: AsyncSession) -> UUID:
    """Ensures a default organization exists."""
    result = await db.execute(
        select(Organization)
        .order_by(Organization.created_at.asc())
        .limit(1)
    )
    organization = result.scalar_one_or_none()

    if organization is not None:
        return organization.id

    organization = Organization(
        name="Main Facility",
        slug="main-facility",
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

    camera = await create_camera(
        db=db,
        camera_data=camera_data,
    )
    return _enrich_camera(camera)


@router.get(
    "/",
    response_model=List[CameraResponse],
)
async def get_all_cameras(
    db: AsyncSession = Depends(get_db),
):
    cameras = await get_cameras(db)

    # If database is fresh and has no cameras yet, auto-provision an initial camera
    if not cameras:
        org_id = await _default_organization_id(db)
        initial_cam = await create_camera(
            db=db,
            camera_data=CameraCreate(
                organization_id=org_id,
                name="Primary Live Camera",
                location="Main Lobby",
                rtsp_url="0",  # Default webcam or test feed
                status="online",
                is_active=True,
                fps=30,
                resolution="1920x1080",
            ),
        )
        cameras = [initial_cam]

    return [_enrich_camera(c) for c in cameras]


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

    return _enrich_camera(camera)


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

    updated = await update_camera(
        db=db,
        camera=camera,
        camera_data=camera_data,
    )
    return _enrich_camera(updated)


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


# --------------------------------------------------------------------------
# Real-Time AI Camera Live Stream (MJPEG with YOLO Detections)
# --------------------------------------------------------------------------

def _generate_annotated_stream(source: str):
    """
    Opens camera stream, runs YOLO detection frame-by-frame,
    draws bounding boxes and metadata, and yields MJPEG frames.
    """
    capture = open_camera_stream(source)

    # Lazy import of models and detection
    try:
        from app.ml.inference_client import detect_objects
        from app.ml.model_registry import person_vehicle_model
        ai_available = True
    except Exception as e:
        logger.warning(f"AI models unavailable for streaming: {e}")
        ai_available = False

    fps_count = 0
    fps_start = time.time()
    current_fps = 0

    try:
        while True:
            success, frame = capture.read()

            if not success:
                # If stream disconnected or video reached end, try reopening or rewind
                capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                success, frame = capture.read()

                if not success:
                    # Synthetic waiting frame
                    frame = 20 * np.ones((480, 640, 3), dtype=np.uint8)
                    cv2.putText(
                        frame,
                        "Connecting to camera stream...",
                        (80, 240),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 200, 255),
                        2,
                    )
                    ret, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                    yield (
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
                    )
                    time.sleep(1.0)
                    continue

            # Run YOLO AI detection on every frame
            if ai_available:
                try:
                    detections = detect_objects(person_vehicle_model, frame, "person_vehicle")
                    for det in detections:
                        bbox = det.get("bbox", {})
                        x1 = int(bbox.get("x1", 0))
                        y1 = int(bbox.get("y1", 0))
                        x2 = int(bbox.get("x2", 0))
                        y2 = int(bbox.get("y2", 0))
                        label = f"{det.get('object_type', 'object')} {det.get('confidence', 0):.0%}"

                        # Draw bounding box
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 60), 2)

                        # Draw label tag with background
                        text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
                        cv2.rectangle(
                            frame,
                            (x1, max(0, y1 - 20)),
                            (x1 + text_size[0] + 6, max(20, y1)),
                            (0, 255, 60),
                            -1,
                        )
                        cv2.putText(
                            frame,
                            label,
                            (x1 + 3, max(15, y1 - 5)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (0, 0, 0),
                            1,
                        )
                except Exception as e:
                    logger.debug(f"Frame detection error: {e}")

            # Calculate FPS
            fps_count += 1
            if time.time() - fps_start >= 1.0:
                current_fps = fps_count
                fps_count = 0
                fps_start = time.time()

            # Render overlay stats: Live badge, timestamp, FPS
            h, w = frame.shape[:2]
            cv2.circle(frame, (25, 25), 6, (0, 0, 255), -1)
            cv2.putText(
                frame,
                f"LIVE • {current_fps} FPS • AI ACTIVE",
                (38, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
            )
            timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(
                frame,
                timestamp_str,
                (w - 200, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (200, 200, 200),
                1,
            )

            # Compress as JPEG for browser streaming
            ret, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if not ret:
                continue

            frame_bytes = buffer.tobytes()
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
            )

            # Cap frame rate to ~25-30 FPS to save CPU
            time.sleep(0.03)

    finally:
        release_camera_stream(capture)


@router.get("/{camera_id}/stream")
async def stream_camera(
    camera_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    camera = await get_camera_from_db(db=db, camera_id=camera_id)
    source = camera.rtsp_url if camera and camera.rtsp_url else "0"

    return StreamingResponse(
        _generate_annotated_stream(source),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@router.get("/stream/live")
async def stream_default_webcam():
    """Direct streaming endpoint for default webcam."""
    return StreamingResponse(
        _generate_annotated_stream("0"),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


# --------------------------------------------------------------------------
# Health & AI Processing Controls
# --------------------------------------------------------------------------

@router.post(
    "/{camera_id}/health/online",
    response_model=CameraResponse,
)
async def mark_camera_as_online(
    camera_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    camera = await get_camera_from_db(db=db, camera_id=camera_id)
    if camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    updated = await mark_camera_online(db=db, camera=camera)
    return _enrich_camera(updated)


@router.post(
    "/{camera_id}/health/offline",
    response_model=CameraResponse,
)
async def mark_camera_as_offline(
    camera_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    camera = await get_camera_from_db(db=db, camera_id=camera_id)
    if camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    updated = await mark_camera_offline(db=db, camera=camera)
    return _enrich_camera(updated)


@router.post(
    "/{camera_id}/health/check",
    response_model=CameraResponse,
)
async def check_camera_health(
    camera_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    camera = await get_camera_from_db(db=db, camera_id=camera_id)
    if camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")

    if not camera.rtsp_url:
        updated = await mark_camera_offline(db=db, camera=camera)
        return _enrich_camera(updated)

    if camera.rtsp_url.strip() in ("0", "webcam") or check_rtsp_stream(camera.rtsp_url):
        updated = await mark_camera_online(db=db, camera=camera)
    else:
        updated = await mark_camera_offline(db=db, camera=camera)

    return _enrich_camera(updated)


@router.post("/{camera_id}/ai/start")
async def start_camera_ai_processing(
    camera_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    camera = await get_camera_from_db(db=db, camera_id=camera_id)
    if camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")

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
