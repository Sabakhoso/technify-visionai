from collections import deque
from typing import Deque, Generator

import numpy as np

from app.ml.inference_client import detect_objects
from app.ml.model_registry import (
    person_vehicle_model,
    ppe_model,
    fire_smoke_model,
    falling_object_model,
    fall_pose_model,
)
from app.services.camera_service import (
    open_camera_stream,
    read_frames,
    release_camera_stream,
)


# Number of recent frames kept in memory.
# At approximately 30 FPS, 150 frames is about 5 seconds.
FRAME_BUFFER_SIZE = 150


def process_camera_stream(
    source: str,
) -> Generator[
    tuple[np.ndarray, list[dict], Deque[np.ndarray]],
    None,
    None,
]:
    capture = open_camera_stream(source)

    frame_buffer: Deque[np.ndarray] = deque(
        maxlen=FRAME_BUFFER_SIZE
    )

    models = [
        (person_vehicle_model, "person_vehicle"),
        (ppe_model, "ppe"),
        (fire_smoke_model, "fire_smoke"),
        (falling_object_model, "falling_object"),
        (fall_pose_model, "fall_pose"),
    ]

    try:
        for frame in read_frames(capture):
            # Keep the most recent frames in memory.
            frame_buffer.append(frame)

            all_detections = []

            for model, model_type in models:
                detections = detect_objects(
                    model,
                    frame,
                    model_type,
                )

                all_detections.extend(detections)

            # Return the current frame, detections,
            # and the rolling frame buffer.
            yield frame, all_detections, frame_buffer

    finally:
        release_camera_stream(capture)