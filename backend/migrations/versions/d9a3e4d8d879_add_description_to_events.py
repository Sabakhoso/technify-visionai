"""add description to events

Revision ID: d9a3e4d8d879
Revises: f4d15c38ddd6
Create Date: 2026-09-03 07:23:56.552658

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d9a3e4d8d879"
down_revision: Union[str, None] = "f4d15c38ddd6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "events",
        sa.Column("description", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("events", "description")