
"""add is_read to alerts

Revision ID: 1e2d16c3783b
Revises: 24cda072f403
Create Date: 2026-09-30 05:54:43.599052
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "1e2d16c3783b"
down_revision: Union[str, None] = "24cda072f403"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "alerts",
        sa.Column(
            "is_read",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )

    op.create_index(
        op.f("ix_alerts_is_read"),
        "alerts",
        ["is_read"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_alerts_is_read"),
        table_name="alerts",
    )

    op.drop_column(
        "alerts",
        "is_read",
    )

