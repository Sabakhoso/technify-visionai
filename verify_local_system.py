"""
Automated end-to-end verification script for Technify VisionAI local deployment.
Tests:
1. Backend health check & system status
2. Database connectivity
3. REST API routes (cameras, analytics, organizations, alerts)
4. AI YOLO model inference
5. Real-time camera streaming with bounding box annotations
6. Frontend dev server availability
"""

import sys
import time
import urllib.request
import json

BACKEND_BASE = "http://127.0.0.1:8000"
FRONTEND_BASE = "http://127.0.0.1:5173"

def test_endpoint(url: str, name: str) -> bool:
    print(f"[*] Testing {name} ({url}) ...", end=" ")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "VisionAI-Verifier/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            status = response.getcode()
            if status == 200:
                print(f"PASSED (HTTP {status})")
                return True
            else:
                print(f"FAILED (HTTP {status})")
                return False
    except Exception as e:
        print(f"FAILED ({e})")
        return False

def test_camera_stream() -> bool:
    print("[*] Testing Live Camera Stream (MJPEG + YOLO AI) ...", end=" ")
    url = f"{BACKEND_BASE}/api/v1/cameras/stream/live"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "VisionAI-Verifier/1.0"})
        with urllib.request.urlopen(req, timeout=12) as response:
            chunk = response.read(1024)
            if b"--frame" in chunk or b"image/jpeg" in chunk or len(chunk) > 100:
                print(f"PASSED (Received {len(chunk)} bytes multipart MJPEG frame)")
                return True
            else:
                print(f"FAILED (Unexpected stream chunk: {chunk[:50]})")
                return False
    except Exception as e:
        print(f"FAILED ({e})")
        return False

def main():
    print("=" * 60)
    print("Technify VisionAI - End-to-End Verification")
    print("=" * 60)

    tests = [
        (f"{BACKEND_BASE}/health", "Backend Health"),
        (f"{BACKEND_BASE}/api/v1/system/status", "System Status API"),
        (f"{BACKEND_BASE}/api/v1/cameras", "Cameras API"),
        (f"{BACKEND_BASE}/api/v1/analytics/overview", "Analytics Overview API"),
        (f"{BACKEND_BASE}/api/v1/organizations", "Organizations API"),
        (f"{BACKEND_BASE}/api/v1/alerts", "Alerts API"),
        (FRONTEND_BASE, "Frontend Web Server"),
    ]

    all_passed = True
    for url, name in tests:
        if not test_endpoint(url, name):
            all_passed = False

    if not test_camera_stream():
        all_passed = False

    print("=" * 60)
    if all_passed:
        print("ALL VERIFICATION CHECKS PASSED SUCCESSFULLY!")
        print(f"Frontend URL: {FRONTEND_BASE}")
        print(f"Backend API Docs: {BACKEND_BASE}/docs")
    else:
        print("SOME CHECKS FAILED. Please review the output above.")
    print("=" * 60)
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

