
"""add evidence table

Revision ID: 24cda072f403

Revises: d9a3e4d8d879

Create Date: 2026-09-25 06:15:40.540821
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "24cda072f403"
down_revision: Union[str, None] = "d9a3e4d8d879"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "evidence",
        sa.Column(
            "event_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "camera_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "evidence_type",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column(
            "file_path",
            sa.String(length=500),
            nullable=False,
        ),
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["camera_id"],
            ["cameras.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["event_id"],
            ["events.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_evidence_camera_id"),
        "evidence",
        ["camera_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_evidence_event_id"),
        "evidence",
        ["event_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_evidence_event_id"),
        table_name="evidence",
    )

    op.drop_index(
        op.f("ix_evidence_camera_id"),
        table_name="evidence",
    )

    op.drop_table("evidence")

