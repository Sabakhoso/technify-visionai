# Technify VisionAI — Local Setup & Camera AI Guide

## 🚀 Quick Start (1-Click)

To run the complete system locally with both frontend and backend:
1. Double-click **`start_all.bat`** in this project folder.
2. It will automatically start:
   - **Backend API**: `http://127.0.0.1:8000`
   - **Frontend UI**: `http://127.0.0.1:5173`
   - Open your browser to the Technify VisionAI dashboard.

Alternatively, you can run services individually:
- **Backend only**: Double-click `run_backend.bat`
- **Frontend only**: Double-click `run_frontend.bat`
- **Run automated system tests**: `backend\.venv\Scripts\python.exe verify_local_system.py`

---

## 📹 Connecting Cameras & AI Object Detection

### 1. Built-in or USB Webcam
- On the **Cameras** page, the default camera is set to source **`0`**.
- This connects directly to your computer's built-in webcam or primary USB camera.
- The AI runs **YOLOv8** on each frame, detecting persons, vehicles, and objects in real-time.
- The stream displays bounding boxes, detection labels, confidence scores, and live FPS directly on the video feed.

### 2. Adding an External or Network (RTSP) Camera
1. Navigate to the **Cameras** tab on the left sidebar.
2. Click **Add Camera**.
3. Enter a friendly name (e.g. `Parking Lot`, `Front Door`).
4. Enter location (e.g. `Building A`).
5. In **Camera Source**, enter either:
   - `0` or `1` for local webcams.
   - `rtsp://username:password@ip_address:554/stream` for IP/RTSP cameras.
   - Path or URL to a video file (e.g., `test_videos/obj_detection.mp4`).
6. Click **Add Camera**. The new camera will instantly appear in the **Live View** grid!

---

## 🧠 AI Models & Detection Capabilities

Technify VisionAI supports multiple specialized vision models powered by YOLO:
- **Person & Vehicle Detection** (`person_vehicle`): Detects pedestrians, cars, trucks, motorcycles, and bicycles with bounding boxes.
- **PPE Compliance Detection** (`ppe`): Detects hardhats, safety vests, masks, and boots.
- **Fire & Smoke Detection** (`fire_smoke`): Detects flame hazards and smoke plumes.
- **Fall Pose Detection** (`fall_pose`): Real-time pose estimation to detect slips, trips, and falls.

Official binary YOLOv8 weights are cached locally in `backend/models/yolov8n.pt`.

---

## 🌐 URLs & Endpoints

| Service | URL | Description |
| :--- | :--- | :--- |
| **Frontend Dashboard** | [http://localhost:5173](http://localhost:5173) | Main React management interface |
| **Live View Grid** | [http://localhost:5173/live-view](http://localhost:5173/live-view) | Multi-camera AI surveillance feeds |
| **API Documentation** | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) | Interactive Swagger UI for all API endpoints |
| **Direct Live Stream** | [http://127.0.0.1:8000/api/v1/cameras/stream/live](http://127.0.0.1:8000/api/v1/cameras/stream/live) | Raw MJPEG stream with YOLO annotations |
| **System Status** | [http://127.0.0.1:8000/api/v1/system/status](http://127.0.0.1:8000/api/v1/system/status) | Operational health of DB and API |

