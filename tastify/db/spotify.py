import enum
from datetime import datetime, timezone

import reflex as rx
import sqlmodel


class SpotifyConnectorState(enum.StrEnum):
    CONNECTING = "connected"
    DISCONNECTED = "disconnected"
    SYNC_DATA = "sync_data"


class SpotifyConnectorTokenType(enum.StrEnum):
    BEARER = "Bearer"


class SpotifyConnector(rx.Model, table=True):
    __tablename__ = "spotify_connector"

    user_uid: str = sqlmodel.Field(foreign_key="user.uid", primary_key=True)
    state: SpotifyConnectorState = sqlmodel.Field(default=SpotifyConnectorState.DISCONNECTED)
    token_type: SpotifyConnectorTokenType = sqlmodel.Field(default=SpotifyConnectorTokenType.BEARER)
    scope: str = sqlmodel.Field(nullable=True)
    access_token: str = sqlmodel.Field(nullable=True)
    code_expires_at: datetime = sqlmodel.Field(sa_type=sqlmodel.DateTime(timezone=True), nullable=True)
    refresh_token: str = sqlmodel.Field(nullable=True)

    def is_expired(self):
        if not self.code_expires_at:
            return True
        return self.code_expires_at.replace(tzinfo=timezone.utc) < datetime.now(tz=timezone.utc)