from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.crud.rule import (
    create_rule,
    delete_rule,
    get_rule,
    get_rules,
    update_rule,
)
from app.schemas.rule import (
    RuleCreate,
    RuleResponse,
    RuleUpdate,
)


router = APIRouter(
    prefix="/rules",
    tags=["Rules"],
)


@router.post(
    "/",
    response_model=RuleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_rule(
    rule_data: RuleCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new detection rule."""
    rule = await create_rule(
        db=db,
        rule_data=rule_data,
    )

    return rule


@router.get(
    "/",
    response_model=List[RuleResponse],
)
async def get_all_rules(
    db: AsyncSession = Depends(get_db),
):
    """Return all detection rules."""
    rules = await get_rules(db=db)

    return rules


@router.get(
    "/{rule_id}",
    response_model=RuleResponse,
)
async def get_single_rule(
    rule_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Return a single detection rule."""
    rule = await get_rule(
        db=db,
        rule_id=rule_id,
    )

    if rule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found",
        )

    return rule


@router.put(
    "/{rule_id}",
    response_model=RuleResponse,
)
async def update_existing_rule(
    rule_id: UUID,
    rule_data: RuleUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing detection rule."""
    rule = await get_rule(
        db=db,
        rule_id=rule_id,
    )

    if rule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found",
        )

    updated_rule = await update_rule(
        db=db,
        rule=rule,
        rule_data=rule_data,
    )

    return updated_rule


@router.delete(
    "/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_existing_rule(
    rule_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete an existing detection rule."""
    rule = await get_rule(
        db=db,
        rule_id=rule_id,
    )

    if rule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found",
        )

    await delete_rule(
        db=db,
        rule=rule,
    )