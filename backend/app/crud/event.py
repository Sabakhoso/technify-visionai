
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event
from app.schemas.event import EventCreate


async def create_event(
    db: AsyncSession,
    event_data: EventCreate,
) -> Event:
    event = Event(**event_data.model_dump())

    db.add(event)

    await db.commit()
    await db.refresh(event)

    return event


async def get_active_event(
    db: AsyncSession,
    camera_id,
    event_type: str,
) -> Event | None:
    result = await db.execute(
        select(Event).where(
            Event.camera_id == camera_id,
            Event.event_type == event_type,
            Event.status == "new",
            Event.end_time.is_(None),
        )
    )

    return result.scalars().first()


async def get_active_events(
    db: AsyncSession,
    camera_id,
) -> list[Event]:
    result = await db.execute(
        select(Event).where(
            Event.camera_id == camera_id,
            Event.status == "new",
            Event.end_time.is_(None),
        )
    )

    return list(result.scalars().all())