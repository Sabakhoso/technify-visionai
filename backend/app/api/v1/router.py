
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
    zone,
)


api_router = APIRouter()


api_router.include_router(
    alerts.router,
    prefix="/alerts",
    tags=["Alerts"],
)

api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["Analytics"],
)

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)

api_router.include_router(
    cameras.router,
    prefix="/cameras",
    tags=["Cameras"],
)

api_router.include_router(
    detections.router,
    prefix="/detections",
    tags=["Detections"],
)

api_router.include_router(
    events.router,
    prefix="/events",
    tags=["Events"],
)

api_router.include_router(
    incidents.router,
    prefix="/incidents",
    tags=["Incidents"],
)

api_router.include_router(
    organizations.router,
    prefix="/organizations",
    tags=["Organizations"],
)

api_router.include_router(
    rules.router,
    prefix="/rules",
    tags=["Rules"],
)

api_router.include_router(
    search.router,
    prefix="/search",
    tags=["Search"],
)

api_router.include_router(
    zone.router,
    prefix="/zones",
    tags=["Zones"],
)

