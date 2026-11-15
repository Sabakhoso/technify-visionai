"""
Alert service for processing security zone breaches, perimeter violations,
and dispatching live alerts across WebSockets and database persistence.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.alert import Alert
from app.models.zone import Zone
from app.services.geometry import get_bottom_center, point_in_polygon
from app.websockets.live_events import manager

logger = logging.getLogger("technify_visionai.alert_service")


async def evaluate_zone_breaches(
    db: AsyncSession,
    camera_id: uuid.UUID,
    organization_id: uuid.UUID,
    detections: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Evaluate real-time object detections against active security zones for a camera.
    Returns a list of detected breach event payloads.
    """
    if not detections:
        return []

    # Fetch active zones for this camera
    query = select(Zone).where(
        Zone.camera_id == camera_id,
        Zone.is_active == True,
    )
    result = await db.execute(query)
    active_zones = result.scalars().all()

    if not active_zones:
        return []

    triggered_breaches = []

    for det in detections:
        bbox = det.get("bbox")
        if not bbox:
            continue

        label = det.get("label", "object")
        confidence = float(det.get("confidence", 0.0))

        # Bottom-center represents ground contact point (e.g., feet of person, wheels of vehicle)
        point = get_bottom_center(bbox)

        for zone in active_zones:
            geometry = zone.geometry
            if not geometry or not isinstance(geometry, list) or len(geometry) < 3:
                continue

            if point_in_polygon(point, geometry):
                breach_payload = {
                    "zone_id": str(zone.id),
                    "zone_name": zone.name,
                    "kind": zone.kind,
                    "camera_id": str(camera_id),
                    "organization_id": str(organization_id),
                    "label": label,
                    "confidence": round(confidence, 3),
                    "point": {"x": round(point[0], 2), "y": round(point[1], 2)},
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                triggered_breaches.append(breach_payload)

                # Persist Alert record
                try:
                    new_alert = Alert(
                        organization_id=organization_id,
                        channel="dashboard",
                        destination=f"zone:{zone.name}",
                        status="sent",
                        is_read=False,
                        sent_at=datetime.now(timezone.utc),
                        error=None,
                    )
                    db.add(new_alert)
                    await db.commit()
                except Exception as exc:
                    await db.rollback()
                    logger.warning(f"Could not persist alert record: {exc}")

                # Broadcast live security alert via WebSockets
                try:
                    await manager.broadcast("alerts", {
                        "type": "security_breach",
                        "severity": "critical" if label == "person" else "warning",
                        "data": breach_payload,
                    })
                except Exception as exc:
                    logger.warning(f"Could not broadcast alert via WebSocket: {exc}")

    return triggered_breaches
