from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rule import Rule
from app.schemas.rule import RuleCreate, RuleUpdate

async def get_matching_rules(
    db: AsyncSession,
    organization_id: UUID,
    camera_id: UUID,
    object_type: str,
) -> list[Rule]:
    result = await db.execute(
        select(Rule).where(
            Rule.organization_id == organization_id,
            Rule.camera_id == camera_id,
            Rule.is_active.is_(True),
        )
    )

    rules = result.scalars().all()

    matching_rules = [
        rule
        for rule in rules
        if object_type in (rule.object_types or [])
    ]

    return matching_rules


async def create_rule(
    db: AsyncSession,
    rule_data: RuleCreate,
) -> Rule:
    rule = Rule(**rule_data.model_dump())

    db.add(rule)
    await db.commit()
    await db.refresh(rule)

    return rule


async def get_rule(
    db: AsyncSession,
    rule_id: UUID,
) -> Rule | None:
    result = await db.execute(
        select(Rule).where(Rule.id == rule_id)
    )

    return result.scalar_one_or_none()


async def get_rules(
    db: AsyncSession,
) -> list[Rule]:
    result = await db.execute(
        select(Rule).order_by(Rule.created_at.desc())
    )

    return list(result.scalars().all())


async def update_rule(
    db: AsyncSession,
    rule: Rule,
    rule_data: RuleUpdate,
) -> Rule:
    update_data = rule_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(rule, field, value)

    await db.commit()
    await db.refresh(rule)

    return rule


async def delete_rule(
    db: AsyncSession,
    rule: Rule,
) -> None:
    await db.delete(rule)
    await db.commit()