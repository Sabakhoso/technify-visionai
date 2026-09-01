from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.rule import Rule


router = APIRouter(
    prefix="/rules",
    tags=["Rules"],
)


@router.get("/", response_model=List[dict])
async def get_rules(
    db: AsyncSession = Depends(get_db),
):
    """Return all detection rules."""

    result = await db.execute(
        select(Rule)
    )

    rules = result.scalars().all()

    return [
        {
            "id": str(rule.id),
            "name": getattr(rule, "name", None),
            "description": getattr(rule, "description", None),
            "enabled": getattr(rule, "enabled", None),
        }
        for rule in rules
    ]


@router.get("/{rule_id}", response_model=dict)
async def get_rule(
    rule_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Return a single rule."""

    result = await db.execute(
        select(Rule).where(Rule.id == rule_id)
    )

    rule = result.scalar_one_or_none()

    if rule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found",
        )

    return {
        "id": str(rule.id),
        "name": getattr(rule, "name", None),
        "description": getattr(rule, "description", None),
        "enabled": getattr(rule, "enabled", None),
    }