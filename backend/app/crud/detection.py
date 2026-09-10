from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.rule import get_matching_rules
from app.models.alert import Alert
from app.models.detection import Detection
from app.models.event import Event
from app.models.incident import Incident
from app.models.zone import Zone
from app.schemas.detection import DetectionCreate
from app.services.geometry import detection_is_inside_zone


async def create_detection(
    db: AsyncSession,
    detection_data: DetectionCreate,
) -> Detection:
    """
    Create a detection and automatically process matching rules.

    Flow:
        Detection
            ↓
        Matching Rule
            ↓
        Zone Check
            ↓
        Event
            ↓
        High/Critical Event
            ↓
        Incident
            ↓
        Dashboard Alert
    """

    detection = Detection(
        **detection_data.model_dump()
    )

    db.add(detection)
    await db.flush()

    # Respect an explicitly supplied event_id.
    if detection.event_id is None:

        matching_rules = await get_matching_rules(
            db=db,
            organization_id=detection.organization_id,
            camera_id=detection.camera_id,
            object_type=detection.object_type,
        )

        for rule in matching_rules:

            # Ignore rules that don't request event creation.
            if "create_event" not in (rule.actions or []):
                continue

            # If the rule has a zone, the detection must be inside it.
            if rule.zone_id is not None:

                result = await db.execute(
                    select(Zone).where(
                        Zone.id == rule.zone_id,
                        Zone.organization_id == detection.organization_id,
                        Zone.camera_id == detection.camera_id,
                        Zone.is_active.is_(True),
                    )
                )

                zone = result.scalar_one_or_none()

                if zone is None:
                    continue

                if not detection_is_inside_zone(
                    bbox=detection.bbox,
                    geometry=zone.geometry,
                ):
                    continue

            # ---------------------------------------------------------
            # 1. Create Event
            # ---------------------------------------------------------

            event = Event(
                organization_id=detection.organization_id,
                camera_id=detection.camera_id,
                event_type=rule.rule_type,
                severity=rule.severity,
                confidence=detection.confidence,
                start_time=detection.detected_at,
                status="new",
                description=(
                    f"Automatic event created by rule "
                    f"'{rule.name}' for detected "
                    f"'{detection.object_type}'."
                ),
            )

            db.add(event)
            await db.flush()

            # Link Detection → Event.
            detection.event_id = event.id

            # ---------------------------------------------------------
            # 2. Create Incident for High/Critical events
            # ---------------------------------------------------------

            if rule.severity.lower() in {"high", "critical"}:

                incident = Incident(
                    organization_id=detection.organization_id,
                    title=rule.name,
                    status="open",
                    severity=rule.severity,
                    summary=(
                        f"Security event '{rule.rule_type}' detected "
                        f"for '{detection.object_type}' by camera "
                        f"{detection.camera_id}."
                    ),
                )

                db.add(incident)
                await db.flush()

                # Link Event → Incident.
                event.incident_id = incident.id

                # -----------------------------------------------------
                # 3. Create Dashboard Alert automatically
                # -----------------------------------------------------

                alert = Alert(
                    organization_id=detection.organization_id,
                    event_id=event.id,
                    incident_id=incident.id,
                    user_id=None,
                    channel="dashboard",
                    destination="security-dashboard",
                    status="pending",
                )

                db.add(alert)
                await db.flush()

            # For now, create only one event per detection.
            break

    await db.commit()
    await db.refresh(detection)

    return detection


async def get_detection(
    db: AsyncSession,
    detection_id: str,
) -> Detection | None:
    result = await db.execute(
        select(Detection).where(
            Detection.id == detection_id
        )
    )

    return result.scalar_one_or_none()


async def get_detections(
    db: AsyncSession,
) -> list[Detection]:
    result = await db.execute(
        select(Detection).order_by(
            Detection.detected_at.desc()
        )
    )

    return list(result.scalars().all())