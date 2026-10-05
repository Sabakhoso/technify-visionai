from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4

import cv2
import numpy as np


# Root directory where event evidence will be stored.
EVIDENCE_ROOT = (
    Path(__file__).resolve().parents[2] / "evidence"
)


def save_event_snapshot(
    frame: np.ndarray,
    camera_id: UUID,
    event_type: str,
    event_id: UUID | None = None,
) -> str:
    """
    Save a camera frame as evidence for an event.

    Args:
        frame:
            OpenCV image frame.

        camera_id:
            ID of the camera that produced the frame.

        event_type:
            Type of event, for example:
            "fire_detection".

        event_id:
            Optional ID of the database event.

    Returns:
        The path of the saved snapshot as a string.

    Raises:
        ValueError:
            If the frame is invalid.

        RuntimeError:
            If OpenCV cannot save the snapshot.
    """

    if frame is None or frame.size == 0:
        raise ValueError(
            "Cannot save evidence: frame is empty."
        )

    timestamp = datetime.now(timezone.utc)

    camera_directory = (
        EVIDENCE_ROOT
        / str(camera_id)
        / event_type
    )

    camera_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp_text = timestamp.strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    event_identifier = (
        str(event_id)
        if event_id is not None
        else str(uuid4())
    )

    filename = (
        f"{timestamp_text}_{event_identifier}.jpg"
    )

    snapshot_path = camera_directory / filename

    success = cv2.imwrite(
        str(snapshot_path),
        frame,
    )

    if not success:
        raise RuntimeError(
            f"Failed to save evidence snapshot: "
            f"{snapshot_path}"
        )

    return str(snapshot_path)
def save_event_video(
    frames: list[np.ndarray],
    camera_id: UUID,
    event_type: str,
    event_id: UUID,
    fps: float = 30.0,
) -> str:
    if not frames:
        raise ValueError("Cannot save evidence video: no frames provided.")

    first_frame = frames[0]

    if first_frame is None or first_frame.size == 0:
        raise ValueError("Cannot save evidence video: first frame is empty.")

    height, width = first_frame.shape[:2]

    timestamp = datetime.now(timezone.utc)

    camera_directory = (
        EVIDENCE_ROOT
        / str(camera_id)
        / event_type
    )

    camera_directory.mkdir(parents=True, exist_ok=True)

    timestamp_text = timestamp.strftime("%Y%m%d_%H%M%S_%f")

    filename = f"{timestamp_text}_{event_id}.mp4"

    video_path = camera_directory / filename

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    writer = cv2.VideoWriter(
        str(video_path),
        fourcc,
        fps,
        (width, height),
    )

    if not writer.isOpened():
        raise RuntimeError(
            f"Failed to create evidence video: {video_path}"
        )

    try:
        for frame in frames:
            if frame is None or frame.size == 0:
                continue

            writer.write(frame)

    finally:
        writer.release()

    if not video_path.exists():
        raise RuntimeError(
            f"Evidence video was not created: {video_path}"
        )

    return str(video_path)

