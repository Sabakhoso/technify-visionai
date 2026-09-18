from typing import Any

from ultralytics import YOLO


def detect_objects(
    model: YOLO,
    frame: Any,
    model_type: str,
) -> list[dict]:
    """
    Run a YOLO model on a single video frame.
    """

    results = model(frame, verbose=False)

    detections = []

    for result in results:
        if result.boxes is None:
            continue

        for box in result.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            x1, y1, x2, y2 = box.xyxy[0].tolist()

            detections.append(
                {
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
            )

    return detections