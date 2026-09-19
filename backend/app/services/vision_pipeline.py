from typing import Generator

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


def process_camera_stream(
    source: str,
) -> Generator[list[dict], None, None]:
    """
    Read frames from a camera stream and run
    all specialized YOLO models.
    """

    capture = open_camera_stream(source)

    models = [
        (person_vehicle_model, "person_vehicle"),
        (ppe_model, "ppe"),
        (fire_smoke_model, "fire_smoke"),
        (falling_object_model, "falling_object"),
        (fall_pose_model, "fall_pose"),
    ]

    try:
        for frame in read_frames(capture):
            all_detections = []

            for model, model_type in models:
                detections = detect_objects(
                    model,
                    frame,
                    model_type,
                )

                all_detections.extend(detections)

            yield all_detections

    finally:
        release_camera_stream(capture)