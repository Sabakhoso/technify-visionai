import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))


import asyncio

from app.core.database import get_db_context
from app.crud.camera import create_camera
from app.schemas.camera import CameraCreate


async def main():
    async with get_db_context() as db:

        camera_data = CameraCreate(
            organization_id="a82eebad-cb01-45a5-9ac4-afc48ac78a12",
            name="AI Test Fire Camera",
            location="Test Video",
            rtsp_url=r".\test_videos\fire-test3.mp4",
            status="online",
            is_active=True,
        )

        camera = await create_camera(
            db=db,
            camera_data=camera_data,
        )

        print("Test camera created successfully")
        print("Camera ID:", camera.id)
        print("Camera URL:", camera.rtsp_url)


asyncio.run(main())