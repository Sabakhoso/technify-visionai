import asyncio

from sqlalchemy import select

from app.core.database import get_db_context
from app.models.camera import Camera


async def main():
    async with get_db_context() as db:
        result = await db.execute(select(Camera))
        cameras = result.scalars().all()

        for camera in cameras:
            print("Camera:", camera.name)
            print("ID:", camera.id)
            print("Organization:", camera.organization_id)
            print("URL:", camera.rtsp_url)
            print("-" * 50)


asyncio.run(main())