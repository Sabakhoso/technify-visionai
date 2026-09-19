from typing import Optional


def create_event(
    detection: dict,
) -> Optional[dict]:
    """
    Convert an AI detection into an event.
    """

    object_type = detection.get("object_type")
    confidence = detection.get("confidence")

    # Fire detection
    if object_type == "fire":
        return {
            "event_type": "fire_detection",
            "severity": "critical",
            "confidence": confidence,
            "description": "Fire detected by AI.",
        }

    # Smoke detection
    if object_type == "smoke":
        return {
            "event_type": "smoke_detection",
            "severity": "high",
            "confidence": confidence,
            "description": "Smoke detected by AI.",
        }

    # Falling object detection
    if object_type == "falling_object":
        return {
            "event_type": "falling_object_detection",
            "severity": "high",
            "confidence": confidence,
            "description": "Potential falling object detected by AI.",
        }

    # Person lying down
    if object_type == "laying":
        return {
            "event_type": "fall_detection",
            "severity": "high",
            "confidence": confidence,
            "description": "Person potentially lying down detected by AI.",
        }

    # PPE violations
    if object_type in {
        "NO-Hardhat",
        "NO-Mask",
        "NO-Safety Vest",
    }:
        return {
            "event_type": "ppe_violation",
            "severity": "high",
            "confidence": confidence,
            "description": f"PPE violation detected: {object_type}.",
        }

    return None