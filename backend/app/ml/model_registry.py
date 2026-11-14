"""
Central model registry for YOLO AI models.
Supports loading specialized models with automated fallback to YOLOv8n.
"""

import logging
from pathlib import Path
from ultralytics import YOLO

logger = logging.getLogger("technify_visionai.models")

# Path to the backend models folder
MODELS_DIR = (
    Path(__file__).resolve().parents[2]
    / "models"
)

_loaded_models = {}


def get_model(model_name: str) -> YOLO:
    """
    Loads custom model weights if available, otherwise falls back
    to standard YOLOv8n.
    """
    if model_name in _loaded_models:
        return _loaded_models[model_name]

    pt_file = MODELS_DIR / f"{model_name}.pt"

    # Only load custom weights if file exists and is actual binary weights (>100KB, not Git LFS text pointer)
    if pt_file.exists() and pt_file.stat().st_size > 100 * 1024:
        try:
            logger.info(f"Loading custom YOLO model: {pt_file.name}")
            model = YOLO(str(pt_file))
            _loaded_models[model_name] = model
            return model
        except Exception as e:
            logger.warning(f"Could not load custom {pt_file.name}: {e}. Falling back to standard YOLO.")

    # Fallback to standard lightweight YOLOv8 (yolov8n.pt)
    logger.info(f"Using standard YOLOv8n model for '{model_name}'")
    model = YOLO("yolov8n.pt")
    _loaded_models[model_name] = model
    return model


class LazyModel:
    """
    Lazy proxy that instantiates the YOLO model on first access.
    Prevents blocking application startup.
    """
    def __init__(self, name: str):
        self.name = name
        self._model = None

    @property
    def model(self) -> YOLO:
        if self._model is None:
            self._model = get_model(self.name)
        return self._model

    def __call__(self, *args, **kwargs):
        return self.model(*args, **kwargs)

    def track(self, *args, **kwargs):
        return self.model.track(*args, **kwargs)

    @property
    def names(self):
        return self.model.names


# Specialized YOLO models (lazily loaded)
person_vehicle_model = LazyModel("person_vehicle")
ppe_model = LazyModel("ppe")
fire_smoke_model = LazyModel("fire_smoke")
falling_object_model = LazyModel("falling_object")
fall_pose_model = LazyModel("fall_pose")
