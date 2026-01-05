"""Initial migration - rooms, players, game_rounds tables

Revision ID: 001_initial
Revises: 
Create Date: 2026-01-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "rooms",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=6), nullable=False),
        sa.Column(
            "status",
            sa.Enum("WAITING", "PLAYING", "FINISHED", name="roomstatus"),
            nullable=False,
        ),
        sa.Column("host_id", sa.Integer(), nullable=True),
        sa.Column("current_round_number", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_rooms_code"), "rooms", ["code"], unique=True)

    op.create_table(
        "players",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("room_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("current_guess", sa.Integer(), nullable=True),
        sa.Column("is_host", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "connected_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["room_id"], ["rooms.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_players_room_id"), "players", ["room_id"], unique=False)

    op.create_table(
        "game_rounds",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("room_id", sa.Integer(), nullable=False),
        sa.Column("round_number", sa.Integer(), nullable=False),
        sa.Column("target_number", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("ACTIVE", "FINISHED", name="roundstatus"),
            nullable=False,
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["room_id"], ["rooms.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_game_rounds_room_id"), "game_rounds", ["room_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_game_rounds_room_id"), table_name="game_rounds")
    op.drop_table("game_rounds")
    op.drop_index(op.f("ix_players_room_id"), table_name="players")
    op.drop_table("players")
    op.drop_index(op.f("ix_rooms_code"), table_name="rooms")
    op.drop_table("rooms")
    
    op.execute("DROP TYPE IF EXISTS roomstatus")
    op.execute("DROP TYPE IF EXISTS roundstatus")

