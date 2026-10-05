import cv2

video_path = "test_videos/test_video1.mp4"

cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Could not open video!")
else:
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print("Video opened successfully<3")
    print("FPS:", fps)
    print("Width:", width)
    print("Height:", height)

cap.release()