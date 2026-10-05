from app.services.vision_pipeline import process_camera_stream

video_path = "test_videos/test_video1.mp4"

frame_count = 0

for frame, detections, frame_buffer in process_camera_stream(video_path):
    frame_count += 1

    if frame_count % 25 == 0:
        print(
            f"Frames: {frame_count} | "
            f"Detections: {len(detections)}"
        )

    if frame_count >= 100:
        break

print("Pipeline test completed.")