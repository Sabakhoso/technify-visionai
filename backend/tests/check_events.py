import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import asyncio

from sqlalchemy import select

from app.core.database import get_db_context
from app.models.event import Event


async def main():
    async with get_db_context() as db:
        result = await db.execute(
            select(Event).order_by(Event.created_at.desc())
        )

        events = result.scalars().all()

        print("Total events:", len(events))

        for event in events:
            print(
                "Event:",
                event.event_type,
                "| Severity:",
                event.severity,
                "| Confidence:",
                event.confidence,
                "| Camera:",
                event.camera_id,
            )


asyncio.run(main())