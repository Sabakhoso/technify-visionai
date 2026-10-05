
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select

from app.crud.camera import get_camera
from app.crud.event import (
    create_event,
    get_active_event,
    get_active_events,
)
from app.crud.alert import create_alert
from app.crud.evidence import create_evidence

from app.models.evidence import EvidenceType
from app.models.zone import Zone

from app.schemas.event import EventCreate
from app.schemas.alert import AlertCreate

from app.services.event_engine import create_event as create_ai_event
from app.services.evidence_service import (
    save_event_snapshot,
    save_event_video,
)
from app.services.vision_pipeline import process_camera_stream


CONFIRMATION_FRAMES = 3
MISS_LIMIT = 5

# Evidence recording settings.
# The current frame buffer provides approximately 5 seconds
# of pre-event footage at 30 FPS.
# This adds 15 seconds of post-event footage.
POST_EVENT_SECONDS = 15

# Loitering settings.
LOITER_THRESHOLD_SECONDS = 3
LOITER_MISS_GRACE_FRAMES = 5


def is_inside_zone(cx, cy, zone):
    x1, y1, x2, y2 = zone
    return x1 <= cx <= x2 and y1 <= cy <= y2


def get_restricted_zone(
    camera_zone,
    frame_width,
    frame_height,
):
    """
    Get the camera's configured restricted zone.

    The zone is expected to be stored as normalized coordinates
    between 0 and 1 with type="restricted".
    """
    if not isinstance(camera_zone, dict):
        return None

    if camera_zone.get("type") != "restricted":
        return None

    required_keys = {"x1", "y1", "x2", "y2"}

    if not required_keys.issubset(camera_zone.keys()):
        return None

    try:
        x1 = float(camera_zone["x1"])
        y1 = float(camera_zone["y1"])
        x2 = float(camera_zone["x2"])
        y2 = float(camera_zone["y2"])

        if not all(
            0 <= value <= 1
            for value in (x1, y1, x2, y2)
        ):
            return None

        return (
            int(x1 * frame_width),
            int(y1 * frame_height),
            int(x2 * frame_width),
            int(y2 * frame_height),
        )

    except (TypeError, ValueError):
        return None


def get_loiter_zone(
    camera_zone,
    frame_width,
    frame_height,
):
    """
    Get the camera's configured loitering zone.

    Zone coordinates are normally stored as normalized values
    between 0 and 1.

    If no valid zone is configured, use the center 50%
    of the frame as the fallback zone.
    """
    if isinstance(camera_zone, dict):
        required_keys = {"x1", "y1", "x2", "y2"}

        if required_keys.issubset(camera_zone.keys()):
            try:
                x1 = float(camera_zone["x1"])
                y1 = float(camera_zone["y1"])
                x2 = float(camera_zone["x2"])
                y2 = float(camera_zone["y2"])

                # Normalized coordinates.
                if all(
                    0 <= value <= 1
                    for value in (x1, y1, x2, y2)
                ):
                    return (
                        int(x1 * frame_width),
                        int(y1 * frame_height),
                        int(y2 * frame_width),
                        int(y2 * frame_height),
                    )

                # Pixel coordinates are also supported.
                return (
                    int(x1),
                    int(y1),
                    int(x2),
                    int(y2),
                )

            except (TypeError, ValueError):
                pass

    # Fallback: center 50% of the frame.
    return (
        int(frame_width * 0.25),
        int(frame_height * 0.25),
        int(frame_width * 0.75),
        int(frame_height * 0.75),
    )


def get_line_points(
    geometry,
    frame_width,
    frame_height,
):
    """
    Convert a line zone's geometry into two pixel coordinates.

    Expected normalized geometry:

        [[x1, y1], [x2, y2]]

    where all values are between 0 and 1.

    Pixel coordinates are also supported.
    """
    if not isinstance(geometry, list):
        return None

    if len(geometry) != 2:
        return None

    try:
        point1 = geometry[0]
        point2 = geometry[1]

        if len(point1) != 2 or len(point2) != 2:
            return None

        x1 = float(point1[0])
        y1 = float(point1[1])
        x2 = float(point2[0])
        y2 = float(point2[1])

        values = (x1, y1, x2, y2)

        # Normalized coordinates.
        if all(0 <= value <= 1 for value in values):
            return (
                (
                    x1 * frame_width,
                    y1 * frame_height,
                ),
                (
                    x2 * frame_width,
                    y2 * frame_height,
                ),
            )

        # Pixel coordinates.
        return (
            (x1, y1),
            (x2, y2),
        )

    except (TypeError, ValueError):
        return None


def get_line_side(
    point,
    line_start,
    line_end,
):
    """
    Determine which side of a line a point is on.

    Returns:
        positive value -> one side
        negative value -> opposite side
        zero            -> exactly on the line
    """
    px, py = point
    x1, y1 = line_start
    x2, y2 = line_end

    return (
        (x2 - x1) * (py - y1)
        - (y2 - y1) * (px - x1)
    )


def has_crossed_line(
    previous_point,
    current_point,
    line_start,
    line_end,
):
    """
    Return True when a tracked person's center moves
    from one side of the line to the other.
    """
    previous_side = get_line_side(
        previous_point,
        line_start,
        line_end,
    )

    current_side = get_line_side(
        current_point,
        line_start,
        line_end,
    )

    # A crossing happens when the signs are different.
    return (
        (previous_side < 0 and current_side > 0)
        or (previous_side > 0 and current_side < 0)
    )


def get_crossing_direction(
    previous_point,
    current_point,
    line_start,
    line_end,
):
    """
    Determine crossing direction relative to the configured line.

    "in":
        movement from the right side of the directed line
        to the left side.

    "out":
        movement from the left side to the right side.

    The exact physical meaning of "in"/"out" depends on how
    the line endpoints are configured.
    """
    previous_side = get_line_side(
        previous_point,
        line_start,
        line_end,
    )

    current_side = get_line_side(
        current_point,
        line_start,
        line_end,
    )

    if previous_side < 0 and current_side > 0:
        return "in"

    if previous_side > 0 and current_side < 0:
        return "out"

    return None


async def create_pending_alert(
    db,
    event,
):
    """
    Create an internal pending alert for a newly created event.

    Notification delivery is not implemented yet.
    The alert is stored as pending so a notification provider
    can be connected later.
    """
    alert_data = AlertCreate(
        organization_id=event.organization_id,
        event_id=event.id,
        incident_id=event.incident_id,
        channel="system",
        destination="internal",
        status="pending",
    )

    return await create_alert(
        db=db,
        alert_data=alert_data,
    )


async def process_camera(
    camera_id: UUID,
) -> None:
    from app.core.database import get_db_context

    async with get_db_context() as db:
        camera = await get_camera(
            db=db,
            camera_id=camera_id,
        )

        if camera is None:
            raise ValueError(
                f"Camera not found: {camera_id}"
            )

        if not camera.rtsp_url:
            raise ValueError(
                f"Camera has no RTSP URL: {camera_id}"
            )

        detection_counts = {}
        miss_counts = {}

        # Loitering state for each tracked person.
        track_zone_start_frame = {}
        track_zone_miss_count = {}
        loitering_ids = set()

        # Stores the previous center point of each tracked
        # person for each line zone.
        previous_line_points = {}

        # Stores video recordings that are currently
        # collecting post-event frames.
        post_event_recordings = {}

        processing_error = False

        try:
            frame_count = 0
            video_fps = camera.fps or 30.0

            frames_needed_for_loiter = int(
                LOITER_THRESHOLD_SECONDS * video_fps
            )

            # Load active line zones for this camera.
            line_zone_result = await db.execute(
                select(Zone).where(
                    Zone.camera_id == camera.id,
                    Zone.is_active.is_(True),
                    Zone.kind == "line",
                )
            )

            line_zones = list(
                line_zone_result.scalars().all()
            )

            for (
                frame,
                detections,
                frame_buffer,
            ) in process_camera_stream(camera.rtsp_url):

                frame_count += 1

                # Get frame dimensions.
                frame_height, frame_width = frame.shape[:2]

                # Use the camera's configured loitering zone.
                loiter_zone = get_loiter_zone(
                    camera.zone,
                    frame_width,
                    frame_height,
                )

                # Get the configured restricted zone.
                restricted_zone = get_restricted_zone(
                    camera.zone,
                    frame_width,
                    frame_height,
                )

                # Continue recording frames for events
                # that have already been confirmed.
                completed_recordings = []

                for event_id, recording in (
                    post_event_recordings.items()
                ):
                    recording["frames"].append(frame)
                    recording["remaining_frames"] -= 1

                    if recording["remaining_frames"] <= 0:
                        completed_recordings.append(event_id)

                # Save completed post-event recordings.
                for event_id in completed_recordings:
                    recording = post_event_recordings.pop(
                        event_id
                    )

                    video_path = save_event_video(
                        frames=recording["frames"],
                        camera_id=camera.id,
                        event_type=recording["event_type"],
                        event_id=event_id,
                        fps=recording["fps"],
                    )

                    await create_evidence(
                        db=db,
                        event_id=event_id,
                        camera_id=camera.id,
                        evidence_type=EvidenceType.VIDEO,
                        file_path=video_path,
                    )

                detected_event_types = set()

                for detection in detections:

                    # -------------------------------------------------
                    # PERSON TRACKING / ZONE-BASED DETECTION
                    # -------------------------------------------------
                    if (
                        detection.get("model_type")
                        == "person_vehicle"
                        and detection.get("object_type")
                        in {"pedestrian", "people"}
                        and detection.get("track_id") is not None
                    ):
                        track_id = detection["track_id"]

                        bbox = detection["bbox"]

                        x1 = bbox["x1"]
                        y1 = bbox["y1"]
                        x2 = bbox["x2"]
                        y2 = bbox["y2"]

                        cx = (x1 + x2) / 2
                        cy = (y1 + y2) / 2

                        current_point = (cx, cy)

                        # -------------------------------------------------
                        # RESTRICTED ZONE DETECTION
                        # -------------------------------------------------
                        restricted_zone_violation = False

                        if restricted_zone is not None:
                            restricted_zone_violation = (
                                is_inside_zone(
                                    cx,
                                    cy,
                                    restricted_zone,
                                )
                            )

                        if restricted_zone_violation:
                            event_type = (
                                "restricted_zone_intrusion"
                            )

                            # Keep this event active while the person
                            # remains inside the restricted zone.
                            detected_event_types.add(
                                event_type
                            )

                            active_event = await get_active_event(
                                db=db,
                                camera_id=camera.id,
                                event_type=event_type,
                            )

                            # Create the event only once.
                            if active_event is None:
                                event = EventCreate(
                                    organization_id=(
                                        camera.organization_id
                                    ),
                                    camera_id=camera.id,
                                    event_type=event_type,
                                    severity="high",
                                    confidence=detection[
                                        "confidence"
                                    ],
                                    start_time=datetime.now(
                                        timezone.utc
                                    ),
                                    status="new",
                                    description=(
                                        f"Person with track ID "
                                        f"{track_id} entered the "
                                        f"restricted zone."
                                    ),
                                )

                                created_event = await create_event(
                                    db=db,
                                    event_data=event,
                                )

                                # Create pending alert.
                                await create_pending_alert(
                                    db=db,
                                    event=created_event,
                                )

                                # Save snapshot evidence.
                                snapshot_path = (
                                    save_event_snapshot(
                                        frame=frame,
                                        camera_id=camera.id,
                                        event_type=event_type,
                                        event_id=created_event.id,
                                    )
                                )

                                await create_evidence(
                                    db=db,
                                    event_id=created_event.id,
                                    camera_id=camera.id,
                                    evidence_type=(
                                        EvidenceType.SNAPSHOT
                                    ),
                                    file_path=snapshot_path,
                                )

                                # Start post-event video recording.
                                fps = camera.fps or 30.0

                                post_event_recordings[
                                    created_event.id
                                ] = {
                                    "frames": list(
                                        frame_buffer
                                    ),
                                    "remaining_frames": int(
                                        fps
                                        * POST_EVENT_SECONDS
                                    ),
                                    "event_type": event_type,
                                    "fps": fps,
                                }

                        # -------------------------------------------------
                        # LINE CROSSING DETECTION
                        # -------------------------------------------------
                        for line_zone in line_zones:
                            line_points = get_line_points(
                                line_zone.geometry,
                                frame_width,
                                frame_height,
                            )

                            if line_points is None:
                                continue

                            line_start, line_end = line_points

                            # Each line has its own tracking history.
                            line_previous_points = (
                                previous_line_points.setdefault(
                                    str(line_zone.id),
                                    {},
                                )
                            )

                            previous_point = (
                                line_previous_points.get(
                                    track_id
                                )
                            )

                            if previous_point is not None:
                                crossed = has_crossed_line(
                                    previous_point,
                                    current_point,
                                    line_start,
                                    line_end,
                                )

                                if crossed:
                                    crossing_direction = (
                                        get_crossing_direction(
                                            previous_point,
                                            current_point,
                                            line_start,
                                            line_end,
                                        )
                                    )

                                    configured_direction = (
                                        line_zone.direction
                                        or "both"
                                    ).lower()

                                    direction_allowed = (
                                        configured_direction
                                        == "both"
                                        or configured_direction
                                        == crossing_direction
                                    )

                                    if direction_allowed:
                                        event_type = (
                                            "line_crossing"
                                        )

                                        # Keep the event active briefly
                                        # after the crossing so repeated
                                        # frames do not create duplicates.
                                        detected_event_types.add(
                                            event_type
                                        )

                                        miss_counts[
                                            event_type
                                        ] = 0

                                        active_event = (
                                            await get_active_event(
                                                db=db,
                                                camera_id=camera.id,
                                                event_type=event_type,
                                            )
                                        )

                                        if active_event is None:
                                            direction_text = (
                                                crossing_direction
                                                or "unknown"
                                            )

                                            event = EventCreate(
                                                organization_id=(
                                                    camera.organization_id
                                                ),
                                                camera_id=camera.id,
                                                event_type=event_type,
                                                severity="high",
                                                confidence=detection[
                                                    "confidence"
                                                ],
                                                start_time=datetime.now(
                                                    timezone.utc
                                                ),
                                                status="new",
                                                description=(
                                                    f"Person with track ID "
                                                    f"{track_id} crossed "
                                                    f"line '{line_zone.name}' "
                                                    f"in the "
                                                    f"{direction_text} "
                                                    f"direction."
                                                ),
                                            )

                                            created_event = (
                                                await create_event(
                                                    db=db,
                                                    event_data=event,
                                                )
                                            )

                                            # Create pending alert.
                                            await create_pending_alert(
                                                db=db,
                                                event=created_event,
                                            )

                                            # Save snapshot evidence.
                                            snapshot_path = (
                                                save_event_snapshot(
                                                    frame=frame,
                                                    camera_id=camera.id,
                                                    event_type=event_type,
                                                    event_id=(
                                                        created_event.id
                                                    ),
                                                )
                                            )

                                            await create_evidence(
                                                db=db,
                                                event_id=(
                                                    created_event.id
                                                ),
                                                camera_id=camera.id,
                                                evidence_type=(
                                                    EvidenceType.SNAPSHOT
                                                ),
                                                file_path=snapshot_path,
                                            )

                                            # Start post-event recording.
                                            fps = camera.fps or 30.0

                                            post_event_recordings[
                                                created_event.id
                                            ] = {
                                                "frames": list(
                                                    frame_buffer
                                                ),
                                                "remaining_frames": int(
                                                    fps
                                                    * POST_EVENT_SECONDS
                                                ),
                                                "event_type": event_type,
                                                "fps": fps,
                                            }

                            # Save current position for the next frame.
                            line_previous_points[track_id] = (
                                current_point
                            )

                        # -------------------------------------------------
                        # LOITERING DETECTION
                        # -------------------------------------------------
                        was_loitering = (
                            track_id in loitering_ids
                        )

                        inside_zone = is_inside_zone(
                            cx,
                            cy,
                            loiter_zone,
                        )

                        if inside_zone:
                            # Person is inside the configured zone.
                            # Start the timer if this is a new track.
                            if (
                                track_id
                                not in track_zone_start_frame
                            ):
                                track_zone_start_frame[
                                    track_id
                                ] = frame_count

                            # Reset temporary missed-frame counter.
                            track_zone_miss_count[
                                track_id
                            ] = 0

                            # Calculate how long the person has
                            # remained inside the zone.
                            zone_frames = (
                                frame_count
                                - track_zone_start_frame[
                                    track_id
                                ]
                                + 1
                            )

                            if (
                                zone_frames
                                >= frames_needed_for_loiter
                            ):
                                loitering_ids.add(
                                    track_id
                                )

                        else:
                            # Person temporarily moved outside the zone.
                            # Give a small grace period before resetting.
                            if (
                                track_id
                                in track_zone_start_frame
                            ):
                                track_zone_miss_count[
                                    track_id
                                ] = (
                                    track_zone_miss_count.get(
                                        track_id,
                                        0,
                                    )
                                    + 1
                                )

                                if (
                                    track_zone_miss_count[
                                        track_id
                                    ]
                                    > LOITER_MISS_GRACE_FRAMES
                                ):
                                    track_zone_start_frame.pop(
                                        track_id,
                                        None,
                                    )

                                    track_zone_miss_count.pop(
                                        track_id,
                                        None,
                                    )

                                    loitering_ids.discard(
                                        track_id
                                    )

                        is_loitering = (
                            track_id in loitering_ids
                        )

                        # Keep the loitering event active while
                        # the person is still considered loitering.
                        if is_loitering:
                            detected_event_types.add(
                                "loitering"
                            )

                        # Trigger only once when the person
                        # first crosses the threshold.
                        if (
                            is_loitering
                            and not was_loitering
                        ):
                            event_type = "loitering"

                            active_event = (
                                await get_active_event(
                                    db=db,
                                    camera_id=camera.id,
                                    event_type=event_type,
                                )
                            )

                            if active_event is None:
                                event = EventCreate(
                                    organization_id=(
                                        camera.organization_id
                                    ),
                                    camera_id=camera.id,
                                    event_type=event_type,
                                    severity="medium",
                                    confidence=detection[
                                        "confidence"
                                    ],
                                    start_time=datetime.now(
                                        timezone.utc
                                    ),
                                    status="new",
                                    description=(
                                        f"Person with track ID "
                                        f"{track_id} is loitering "
                                        f"inside the configured "
                                        f"zone."
                                    ),
                                )

                                created_event = await create_event(
                                    db=db,
                                    event_data=event,
                                )

                                # Create pending alert.
                                await create_pending_alert(
                                    db=db,
                                    event=created_event,
                                )

                                # Save snapshot evidence.
                                snapshot_path = (
                                    save_event_snapshot(
                                        frame=frame,
                                        camera_id=camera.id,
                                        event_type=event_type,
                                        event_id=created_event.id,
                                    )
                                )

                                await create_evidence(
                                    db=db,
                                    event_id=created_event.id,
                                    camera_id=camera.id,
                                    evidence_type=(
                                        EvidenceType.SNAPSHOT
                                    ),
                                    file_path=snapshot_path,
                                )

                                # Start post-event video recording.
                                fps = camera.fps or 30.0

                                post_event_recordings[
                                    created_event.id
                                ] = {
                                    "frames": list(
                                        frame_buffer
                                    ),
                                    "remaining_frames": int(
                                        fps
                                        * POST_EVENT_SECONDS
                                    ),
                                    "event_type": event_type,
                                    "fps": fps,
                                }

                        continue

                    # -------------------------------------------------
                    # EXISTING AI EVENTS
                    # -------------------------------------------------
                    event_data = create_ai_event(
                        detection
                    )

                    if event_data is None:
                        continue

                    event_type = event_data["event_type"]

                    detected_event_types.add(
                        event_type
                    )

                    miss_counts[event_type] = 0

                    detection_counts[event_type] = (
                        detection_counts.get(
                            event_type,
                            0,
                        )
                        + 1
                    )

                    active_event = await get_active_event(
                        db=db,
                        camera_id=camera.id,
                        event_type=event_type,
                    )

                    if active_event is not None:
                        continue

                    if (
                        detection_counts[event_type]
                        < CONFIRMATION_FRAMES
                    ):
                        continue

                    event = EventCreate(
                        organization_id=(
                            camera.organization_id
                        ),
                        camera_id=camera.id,
                        event_type=event_type,
                        severity=event_data["severity"],
                        confidence=event_data["confidence"],
                        start_time=datetime.now(
                            timezone.utc
                        ),
                        status="new",
                        description=event_data[
                            "description"
                        ],
                    )

                    created_event = await create_event(
                        db=db,
                        event_data=event,
                    )

                    # Create pending alert.
                    await create_pending_alert(
                        db=db,
                        event=created_event,
                    )

                    # Save snapshot evidence using
                    # the frame that confirmed the event.
                    snapshot_path = save_event_snapshot(
                        frame=frame,
                        camera_id=camera.id,
                        event_type=event_type,
                        event_id=created_event.id,
                    )

                    await create_evidence(
                        db=db,
                        event_id=created_event.id,
                        camera_id=camera.id,
                        evidence_type=EvidenceType.SNAPSHOT,
                        file_path=snapshot_path,
                    )

                    # Start post-event video recording.
                    fps = camera.fps or 30.0

                    post_event_recordings[
                        created_event.id
                    ] = {
                        "frames": list(
                            frame_buffer
                        ),
                        "remaining_frames": int(
                            fps
                            * POST_EVENT_SECONDS
                        ),
                        "event_type": event_type,
                        "fps": fps,
                    }

                # -------------------------------------------------
                # RESOLVE ACTIVE EVENTS
                # -------------------------------------------------
                active_events = await get_active_events(
                    db=db,
                    camera_id=camera.id,
                )

                for active_event in active_events:
                    event_type = active_event.event_type

                    if event_type in detected_event_types:
                        miss_counts[event_type] = 0
                        continue

                    miss_counts[event_type] = (
                        miss_counts.get(
                            event_type,
                            0,
                        )
                        + 1
                    )

                    if miss_counts[event_type] < MISS_LIMIT:
                        continue

                    active_event.end_time = datetime.now(
                        timezone.utc
                    )

                    active_event.status = "resolved"

                    miss_counts[event_type] = 0
                    detection_counts[event_type] = 0

                await db.commit()

        except Exception as e:
            processing_error = True

            print(
                "PROCESS CAMERA ERROR:",
                repr(e),
            )

            await db.rollback()
            raise

        finally:
            if not processing_error:
                try:
                    active_events = await get_active_events(
                        db=db,
                        camera_id=camera.id,
                    )

                    if active_events:
                        end_time = datetime.now(
                            timezone.utc
                        )

                        for active_event in active_events:
                            active_event.end_time = end_time
                            active_event.status = "resolved"

                        await db.commit()

                except Exception:
                    await db.rollback()
