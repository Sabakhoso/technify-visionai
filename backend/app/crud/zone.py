from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.zone import Zone
from app.schemas.zone import ZoneCreate, ZoneUpdate


async def create_zone(
    db: AsyncSession,
    zone_data: ZoneCreate,
) -> Zone:
    zone = Zone(**zone_data.model_dump())

    db.add(zone)
    await db.commit()
    await db.refresh(zone)

    return zone


async def get_zone(
    db: AsyncSession,
    zone_id: UUID,
) -> Zone | None:
    result = await db.execute(
        select(Zone).where(Zone.id == zone_id)
    )

    return result.scalar_one_or_none()


async def get_zones(
    db: AsyncSession,
) -> list[Zone]:
    result = await db.execute(
        select(Zone).order_by(Zone.created_at.desc())
    )

    return list(result.scalars().all())


async def update_zone(
    db: AsyncSession,
    zone: Zone,
    zone_data: ZoneUpdate,
) -> Zone:
    update_data = zone_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(zone, field, value)

    await db.commit()
    await db.refresh(zone)

    return zone


async def delete_zone(
    db: AsyncSession,
    zone: Zone,
) -> None:
    await db.delete(zone)
    await db.commit()