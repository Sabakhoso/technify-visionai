from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.organization import Organization


router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)


@router.get("/", response_model=List[dict])
async def get_organizations(
    db: AsyncSession = Depends(get_db),
):
    """Return all organizations."""

    result = await db.execute(
        select(Organization)
    )

    organizations = result.scalars().all()

    return [
        {
            "id": str(organization.id),
            "name": getattr(organization, "name", None),
            "description": getattr(organization, "description", None),
        }
        for organization in organizations
    ]


@router.get("/{organization_id}", response_model=dict)
async def get_organization(
    organization_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Return a single organization."""

    result = await db.execute(
        select(Organization).where(
            Organization.id == organization_id
        )
    )

    organization = result.scalar_one_or_none()

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    return {
        "id": str(organization.id),
        "name": getattr(organization, "name", None),
        "description": getattr(organization, "description", None),
    }