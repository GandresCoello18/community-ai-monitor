"""Add daily_summaries table

Revision ID: 002_daily_summaries
Revises: 001_initial_schema
Create Date: 2026-07-10

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002_daily_summaries"
down_revision: str | None = "001_initial_schema"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "daily_summaries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("summary_text", sa.Text(), nullable=False),
        sa.Column("total_events", sa.Integer(), nullable=False),
        sa.Column("llm_provider", sa.String(length=64), nullable=False),
        sa.Column("llm_model", sa.String(length=120), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_daily_summaries")),
    )
    op.create_index(
        "idx_daily_summaries_period_start",
        "daily_summaries",
        ["period_start"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_daily_summaries_period_start", table_name="daily_summaries")
    op.drop_table("daily_summaries")
