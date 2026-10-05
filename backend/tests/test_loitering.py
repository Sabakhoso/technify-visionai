from app.services.vision_pipeline import process_camera_stream


VIDEO_PATH = "test_videos/test_video1.mp4"

LOITER_THRESHOLD_SECONDS = 3
VIDEO_FPS = 25.0

zone_x1 = int(3840 * 0.25)
zone_y1 = int(2160 * 0.25)
zone_x2 = int(3840 * 0.75)
zone_y2 = int(2160 * 0.75)

LOITER_ZONE = (zone_x1, zone_y1, zone_x2, zone_y2)


def is_inside_zone(cx, cy, zone):
    x1, y1, x2, y2 = zone
    return x1 <= cx <= x2 and y1 <= cy <= y2


frames_needed = int(LOITER_THRESHOLD_SECONDS * VIDEO_FPS)

track_zone_frame_count = {}
loitering_ids = set()

frame_count = 0

for frame, detections, frame_buffer in process_camera_stream(VIDEO_PATH):

    frame_count += 1

    for detection in detections:

        if (
            detection.get("model_type") == "person_vehicle"
            and detection.get("object_type") in {"pedestrian", "people"}
            and detection.get("track_id") is not None
        ):
            track_id = detection["track_id"]

            bbox = detection["bbox"]

            cx = (bbox["x1"] + bbox["x2"]) / 2
            cy = (bbox["y1"] + bbox["y2"]) / 2

            if is_inside_zone(cx, cy, LOITER_ZONE):

                track_zone_frame_count[track_id] = (
                    track_zone_frame_count.get(track_id, 0) + 1
                )

                if track_zone_frame_count[track_id] >= frames_needed:
                    if track_id not in loitering_ids:
                        loitering_ids.add(track_id)

                        print(
                            f"LOITERING DETECTED | "
                            f"Track ID: {track_id} | "
                            f"Frame: {frame_count} | "
                            f"Time: {frame_count / VIDEO_FPS:.2f}s"
                        )

            else:
                track_zone_frame_count[track_id] = 0

    if frame_count % 25 == 0:
        print(
            f"Frames: {frame_count} | "
            f"Tracked humans: {len(track_zone_frame_count)} | "
            f"Loitering IDs: {sorted(loitering_ids)}"
        )

print()
print("Loitering test completed.")
print(f"Total frames processed: {frame_count}")
print(f"Loitering IDs detected: {sorted(loitering_ids)}")