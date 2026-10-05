
from typing import Any

from ultralytics import YOLO


def detect_objects(
    model: YOLO,
    frame: Any,
    model_type: str,
) -> list[dict]:
    """
    Run a YOLO model on a single video frame.

    Person detections use ByteTrack so a stable track_id
    can be returned for loitering detection.
    """

    if model_type == "person_vehicle":
        results = model.track(
            frame,
            tracker="bytetrack.yaml",
            persist=True,
            verbose=False,
        )
    else:
        results = model(frame, verbose=False)

    detections = []

    for result in results:
        if result.boxes is None:
            continue

        for box in result.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            detection = {
                "model_type": model_type,
                "object_type": model.names[class_id],
                "confidence": confidence,
                "bbox": {
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2,
                },
            }

            # ByteTrack provides track IDs for tracked detections.
            if (
                model_type == "person_vehicle"
                and box.id is not None
            ):
                detection["track_id"] = int(box.id[0])

            detections.append(detection)

    return detections

