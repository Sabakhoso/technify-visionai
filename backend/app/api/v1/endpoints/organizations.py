from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.organization import Organization
from app.schemas.organization import OrganizationResponse, OrganizationUpdate


router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.get("/", response_model=List[OrganizationResponse])
async def get_organizations(db: AsyncSession = Depends(get_db)):
    """Return all organizations."""
    result = await db.execute(select(Organization).order_by(Organization.created_at.asc()))
    return list(result.scalars().all())


@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(organization_id: UUID, db: AsyncSession = Depends(get_db)):
    """Return a single organization."""
    result = await db.execute(select(Organization).where(Organization.id == organization_id))
    organization = result.scalar_one_or_none()
    if organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return organization


@router.patch("/{organization_id}", response_model=OrganizationResponse)
async def update_organization(
    organization_id: UUID,
    payload: OrganizationUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an organization's name, timezone, or settings."""
    result = await db.execute(select(Organization).where(Organization.id == organization_id))
    organization = result.scalar_one_or_none()
    if organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(organization, field, value)

    await db.commit()
    await db.refresh(organization)
    return organization