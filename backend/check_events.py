import asyncio
from sqlalchemy import select
from app.core.database import get_db_context
from app.models.event import Event


async def main():
    async with get_db_context() as db:
        result = await db.execute(
            select(Event)
            .where(
                Event.camera_id == "1b5b5b17-2a80-4cb2-92f1-0a67fc287582",
                Event.event_type == "fire_detection",
            )
            .order_by(Event.created_at.desc())
            .limit(5)
        )

        for event in result.scalars():
            print(
                "ID:", event.id,
                "| Status:", event.status,
                "| Start:", event.start_time,
                "| End:", event.end_time,
                "| Created:", event.created_at,
            )


asyncio.run(main())