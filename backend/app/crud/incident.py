from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incident import Incident
from app.schemas.incident import IncidentCreate, IncidentUpdate


async def create_incident(
    db: AsyncSession,
    incident_data: IncidentCreate,
) -> Incident:
    """
    Create a new incident.
    """
    incident = Incident(
        **incident_data.model_dump()
    )

    db.add(incident)
    await db.commit()
    await db.refresh(incident)

    return incident


async def get_incident(
    db: AsyncSession,
    incident_id: UUID,
) -> Incident | None:
    """
    Get a single incident by ID.
    """
    result = await db.execute(
        select(Incident).where(
            Incident.id == incident_id
        )
    )

    return result.scalar_one_or_none()


async def get_incidents(
    db: AsyncSession,
) -> list[Incident]:
    """
    Get all incidents, newest first.
    """
    result = await db.execute(
        select(Incident).order_by(
            Incident.created_at.desc()
        )
    )

    return list(result.scalars().all())


async def update_incident(
    db: AsyncSession,
    incident: Incident,
    incident_data: IncidentUpdate,
) -> Incident:
    """
    Update an existing incident.
    """
    update_data = incident_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(incident, field, value)

    await db.commit()
    await db.refresh(incident)

    return incident


async def delete_incident(
    db: AsyncSession,
    incident: Incident,
) -> None:
    """
    Delete an existing incident.
    """
    await db.delete(incident)
    await db.commit()