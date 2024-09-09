import asyncio

import reflex as rx
from sqlmodel import select

from tastify.apps.common.state import CommonState
from tastify.apps.router import Router
from tastify.core.integration.spotify.client import SpotifyClient, UserTokenData, UserTrack
from tastify import db


class SpotifyState(rx.State):
    state: db.SpotifyConnectorState = db.SpotifyConnectorState.DISCONNECTED

    async def connect(self):
        """Connect to Spotify."""
        client = SpotifyClient()
        common = await self.get_state(CommonState)
        return rx.redirect(client.build_authorize_url(state=common.get_client_uid()))

    async def register(self):
        """Register with Spotify."""

        print("register")
        client = SpotifyClient()
        code: str = self.router.page.params.get("code", None)
        user_uid = self.router.page.params.get("state", None)
        error = self.router.page.params.get("error", None)

        common = await self.get_state(CommonState)
        if user_uid != common.get_client_uid():
            raise ValueError("Invalid user")

        if not code:
            raise ValueError(f"The authorization code not found")

        if error:
            raise ValueError("Error registering with Spotify")

        with rx.session() as session:
            connector = get_or_create_connector(
                session=session,
                user_uid=common.get_client_uid(),
            )
            yield

            user_token_data = client.get_user_token(code=code)
            print(user_token_data)
            self.state = connector.state = db.SpotifyConnectorState.SYNC_DATA
            connector.scope = user_token_data.scope
            connector.access_token = user_token_data.access_token
            connector.code_expires_at = user_token_data.expires_at
            connector.refresh_token = user_token_data.refresh_token
            session.commit()

            yield
            await asyncio.sleep(1)
            print('redirecting to home')
            yield Router.to_home()


def get_or_create_connector(session, user_uid) -> db.SpotifyConnector:
    """Get or create a connector."""
    connector = session.exec(select(db.SpotifyConnector).where(db.SpotifyConnector.user_uid == user_uid)).first()
    if not connector:
        connector = db.SpotifyConnector(
            user_uid=user_uid,
        )
        session.add(connector)
        session.commit()
    return connector


class SpotifyListUserTracksState(rx.State):
    state: db.SpotifyConnectorState = db.SpotifyConnectorState.DISCONNECTED
    show_tracks: bool = False
    tracks: list[UserTrack] = []

    async def load_tracks(self):
        """Load user's tracks."""
        client = SpotifyClient()
        common = await self.get_state(CommonState)
        with rx.session() as session:
            connector = get_or_create_connector(session, common.get_client_uid())
            print(connector)
            if connector.is_expired():
                self.state = db.SpotifyConnectorState.DISCONNECTED
                return
        self.tracks = client.get_user_tracks(to_user_token_data(connector))
        self.state = connector.state
        print(f'Loaded {len(self.tracks)} tracks')


def to_user_token_data(connector: db.SpotifyConnector) -> UserTokenData:
    return UserTokenData(
        access_token=connector.access_token,
        token_type=connector.token_type.value,
        scope=connector.scope,
        expires_at=connector.code_expires_at,
        refresh_token=connector.refresh_token,
    )