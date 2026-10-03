from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.config import settings
from app.core.database import check_database_connection
from app.models.camera import Camera
from app.models.organization import Organization


router = APIRouter(prefix="/system", tags=["System"])


@router.get("/status")
async def get_system_status(db: AsyncSession = Depends(get_db)):
    """Aggregate health snapshot: API, database, and camera fleet status."""
    db_ok = await check_database_connection()

    total_result = await db.execute(select(func.count()).select_from(Camera))
    total_cameras = total_result.scalar_one()

    online_result = await db.execute(
        select(func.count()).select_from(Camera).where(Camera.status == "online")
    )
    online_cameras = online_result.scalar_one()

    org_result = await db.execute(select(func.count()).select_from(Organization))
    organization_count = org_result.scalar_one()

    return {
        "api": "running",
        "environment": settings.ENVIRONMENT,
        "database": "connected" if db_ok else "disconnected",
        "cameras": {
            "total": total_cameras,
            "online": online_cameras,
            "offline": total_cameras - online_cameras,
        },
        "organizations": organization_count,
    }