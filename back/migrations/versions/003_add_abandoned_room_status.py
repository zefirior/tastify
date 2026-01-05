"""Add abandoned status to room status enum

Revision ID: 003_add_abandoned_status
Revises: 002_add_updated_at
Create Date: 2026-01-05

"""
from typing import Sequence, Union

from alembic import op


revision: str = "003_add_abandoned_status"
down_revision: Union[str, None] = "002_add_updated_at"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add 'abandoned' value to the roomstatus enum
    op.execute("ALTER TYPE roomstatus ADD VALUE IF NOT EXISTS 'abandoned'")


def downgrade() -> None:
    # PostgreSQL doesn't support removing enum values directly
    # We would need to recreate the enum type to remove the value
    # For safety, we leave this as a no-op
    pass

