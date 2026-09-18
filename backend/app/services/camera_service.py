import cv2
from typing import Generator


def open_camera_stream(source: str) -> cv2.VideoCapture:
    """
    Open a video file, webcam, or RTSP camera stream.
    """
    capture = cv2.VideoCapture(source)

    if not capture.isOpened():
        raise RuntimeError(f"Unable to open camera stream: {source}")

    return capture


def read_frames(
    capture: cv2.VideoCapture,
) -> Generator:
    """
    Read frames continuously from an opened camera stream.
    """
    while True:
        success, frame = capture.read()

        if not success:
            break

        yield frame


def release_camera_stream(
    capture: cv2.VideoCapture,
) -> None:
    """
    Release the camera/video stream.
    """
    capture.release()