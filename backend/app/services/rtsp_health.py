import cv2


def check_rtsp_stream(
    rtsp_url: str,
    timeout_seconds: int = 5,
) -> bool:
    """
    Check whether an RTSP stream can be opened and
    whether a video frame can be read.

    Returns:
        True  -> stream is reachable and a frame was read
        False -> stream could not be opened/read
    """

    if not rtsp_url:
        return False

    timeout_milliseconds = timeout_seconds * 1000

    capture = cv2.VideoCapture()

    try:
        # These timeout properties are supported by OpenCV's
        # FFmpeg backend and prevent long RTSP waits.
        capture.set(
            cv2.CAP_PROP_OPEN_TIMEOUT_MSEC,
            timeout_milliseconds,
        )

        capture.set(
            cv2.CAP_PROP_READ_TIMEOUT_MSEC,
            timeout_milliseconds,
        )

        opened = capture.open(
            rtsp_url,
            cv2.CAP_FFMPEG,
        )

        if not opened or not capture.isOpened():
            return False

        success, _ = capture.read()

        return bool(success)

    except Exception:
        return False

    finally:
        capture.release()