import logging
import time
from typing import Generator, Union
import cv2
import numpy as np

logger = logging.getLogger("technify_visionai.camera")


def open_camera_stream(source: Union[str, int]) -> cv2.VideoCapture:
    """
    Open a video file, webcam index, or RTSP camera stream.
    Supports integer indices (0, 1), numeric strings ("0"), RTSP, HTTP, or video paths.
    """
    parsed_source = source
    if isinstance(source, str):
        source_clean = source.strip()
        if source_clean.isdigit():
            parsed_source = int(source_clean)
        elif source_clean.lower() in ("webcam", "default", "camera"):
            parsed_source = 0

    capture = cv2.VideoCapture(parsed_source)

    if not capture.isOpened():
        logger.warning(f"Could not open stream for source: {source}. Trying fallback webcam 0.")
        if parsed_source != 0:
            capture = cv2.VideoCapture(0)

    return capture


def read_frames(capture: cv2.VideoCapture) -> Generator[np.ndarray, None, None]:
    """
    Read frames continuously from an opened camera stream.
    If the physical stream ends (e.g. video file loop), it rewinds or yields a generated frame.
    """
    fps = capture.get(cv2.CAP_PROP_FPS) or 30.0
    frame_interval = 1.0 / fps

    while True:
        start_time = time.time()
        success, frame = capture.read()

        if not success:
            # If video file reached the end, rewind to beginning
            capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            success, frame = capture.read()
            if not success:
                # Generate a synthetic test frame if camera stream is unavailable
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(
                    frame,
                    "Camera Stream Offline / Connecting...",
                    (50, 240),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2,
                )
                yield frame
                time.sleep(1.0)
                continue

        yield frame

        elapsed = time.time() - start_time
        sleep_time = frame_interval - elapsed
        if sleep_time > 0.001:
            time.sleep(sleep_time)


def release_camera_stream(capture: cv2.VideoCapture) -> None:
    """Release the camera/video stream."""
    try:
        capture.release()
    except Exception:
        pass
