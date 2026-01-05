"""Add game_type column to rooms table

Revision ID: 004
Revises: 003_add_abandoned_room_status
Create Date: 2026-01-05

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "004_add_game_type"
down_revision: Union[str, None] = "003_add_abandoned_status"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "rooms",
        sa.Column("game_type", sa.String(50), nullable=False, server_default="guess_number"),
    )
    op.create_index("ix_rooms_game_type", "rooms", ["game_type"])


def downgrade() -> None:
    op.drop_index("ix_rooms_game_type", table_name="rooms")
    op.drop_column("rooms", "game_type")

