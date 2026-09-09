from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.crud.detection import (
    create_detection,
    get_detection,
    get_detections,
)
from app.models.detection import Detection
from app.schemas.detection import DetectionCreate, DetectionResponse


router = APIRouter(
    prefix="/detections",
    tags=["Detections"],
)


@router.post(
    "/",
    response_model=DetectionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_detection(
    detection_data: DetectionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new AI detection."""
    detection = await create_detection(
        db=db,
        detection_data=detection_data,
    )

    return detection


@router.get(
    "/",
    response_model=List[DetectionResponse],
)
async def get_all_detections(
    db: AsyncSession = Depends(get_db),
):
    """Return all AI detections."""
    detections = await get_detections(db=db)

    return detections


@router.get(
    "/{detection_id}",
    response_model=DetectionResponse,
)
async def get_single_detection(
    detection_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Return a single AI detection."""
    detection = await get_detection(
        db=db,
        detection_id=detection_id,
    )

    if detection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detection not found",
        )

    return detection