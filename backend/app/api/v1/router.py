from fastapi import APIRouter

from app.api.v1.endpoints import (
    alerts,
    analytics,
    auth,
    cameras,
    detections,
    events,
    incidents,
    organizations,
    rules,
    search,
    system,
    zone,
)
from app.websockets.live_events import ws_router

api_router = APIRouter()

# Note: Each submodule endpoint file defines its own prefix
# (e.g. alerts.py defines prefix="/alerts"), so we include them directly
# without duplicating the prefix.
api_router.include_router(alerts.router)
api_router.include_router(analytics.router)
api_router.include_router(auth.router)
api_router.include_router(cameras.router)
api_router.include_router(detections.router)
api_router.include_router(events.router)
api_router.include_router(incidents.router)
api_router.include_router(organizations.router)
api_router.include_router(rules.router)
api_router.include_router(search.router)
api_router.include_router(system.router)
api_router.include_router(zone.router, prefix="/zones")
api_router.include_router(ws_router)
