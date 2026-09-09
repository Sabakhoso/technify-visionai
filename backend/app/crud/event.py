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