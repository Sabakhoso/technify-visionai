from pathlib import Path

from ultralytics import YOLO


# Path to the backend models folder
MODELS_DIR = (
    Path(__file__).resolve().parents[2]
    / "models"
)


# Load each specialized YOLO model
person_vehicle_model = YOLO(
    str(MODELS_DIR / "person_vehicle.pt")
)

ppe_model = YOLO(
    str(MODELS_DIR / "ppe.pt")
)

fire_smoke_model = YOLO(
    str(MODELS_DIR / "fire_smoke.pt")
)

falling_object_model = YOLO(
    str(MODELS_DIR / "falling_object.pt")
)

fall_pose_model = YOLO(
    str(MODELS_DIR / "fall_pose.pt")
)