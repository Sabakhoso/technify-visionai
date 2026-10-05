
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evidence import Evidence, EvidenceType


async def create_evidence(
    db: AsyncSession,
    event_id: UUID,
    camera_id: UUID,
    evidence_type: EvidenceType,
    file_path: str,
) -> Evidence:
    evidence = Evidence(
        event_id=event_id,
        camera_id=camera_id,
        evidence_type=evidence_type,
        file_path=file_path,
    )

    db.add(evidence)

    await db.commit()
    await db.refresh(evidence)

    return evidence
