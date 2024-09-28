import asyncio
import logging

import reflex as rx
import sqlmodel
from sqlmodel import select

from tastify import db
from tastify.core.integration.spotify.client import SpotifyClient
from tastify.core.misc import smallest_image
from tastify.domain.common.state import CommonState
from tastify.domain.router import Router

logger = logging.getLogger(__name__)

TRANSITION_MAP = {
    db.GameState.NEW: db.GameState.PREPARING,
    db.GameState.PREPARING: db.GameState.PROPOSE,
    db.GameState.PROPOSE: db.GameState.GUESS,
    db.GameState.GUESS: db.GameState.RESULTS,
    db.GameState.RESULTS: db.GameState.PREPARING,
}


class GameDto(rx.Base):
    id: int
    state: db.GameState
    round: int
    created_by: str


class UserGameDto(rx.Base):
    user_uid: str
    name: str
    score: int


class ArtistDto(rx.Base):
    id: str
    name: str
    image_url: str
    genres: list[str]


def _map_game(game: db.Game):
    return GameDto(
        id=game.id,
        state=game.state,
        round=game.round,
        created_by=game.created_by,
    )


def _map_players(players: list[db.UserGame]):
    return [
        UserGameDto(
            user_uid=player.user_uid,
            name=player.name,
            score=player.score,
        ) for player in players
    ]


class GameState(rx.State):
    game: GameDto = None
    game_state: db.GameState = db.GameState.NEW
    players: list[UserGameDto] = []
    is_current_player: bool = False
    is_dashboard: bool = False
    artist: str = ""

    @rx.var
    def room_code(self) -> str | None:
        return self.router.page.params.get("room_code", None)

    async def refresh_game(self):
        if self.router.page.path != Router.GAME_PATH:
            logger.info("Not in game page")
            return
        await self.load_state()
        await asyncio.sleep(1)
        yield GameState.refresh_game

    async def load_state(self):
        """Load a game."""
        with rx.session() as session:
            db_game = self._fetch_game(session)
            self.game = _map_game(db_game)
            self.game_state = self.game.state
            self.players = _map_players(self._fetch_players(session))

            common = await self.get_state(CommonState)
            user_uid = common.get_client_uid()
            player = next((player for player in self.players if player.user_uid == user_uid), None)
            current_player = self.get_current_player()
            self.is_current_player = player == current_player
            self.is_dashboard = user_uid == self.game.created_by
            self.artist = db_game.data.get("artist", {}).get("name", "")

    def _fetch_players(self, session: sqlmodel.Session):
        return list(session.exec(
            select(
                db.UserGame
            ).join(
                db.Game,
                db.Game.id == db.UserGame.game_id
            ).where(db.Game.id == self.game.id)
        ).all())

    def _fetch_game(self, session: sqlmodel.Session) -> db.Game:
        game = session.exec(
            select(db.Game).join(
                db.Room, db.Room.id == db.Game.room_id,
            ).order_by(
                db.Game.created_at,
            ).where(
                db.Room.code == self.room_code,
            )
        ).first()
        if not game:
            raise ValueError("Game not found")
        return game

    def get_current_player(self):
        current_player_index = self.game.round % len(self.players)
        return sorted(
            self.players,
            key=lambda player: player.user_uid,
        )[current_player_index]

    def move_game_state(self):
        logger.info(f"Moving game state from {self.game_state} to {TRANSITION_MAP[self.game_state]}")
        with rx.session() as session:
            # TODO: resolve data race
            game = self._fetch_game(session)
            if not game:
                # TODO: handle errors in middleware
                raise ValueError("Game not found")
            game.state = TRANSITION_MAP[game.state]
            session.add(game)
            session.commit()

    def select_artist(self, artist):
        logger.info(f"Selected artist {artist['name']}")
        self.load_state()
        if not self.is_current_player:
            logger.info("Not the current player")
            return
        if self.game_state != db.GameState.PROPOSE:
            logger.info("Not in propose state")
            return

        with rx.session() as session:
            # TODO: resolve data race
            game = self._fetch_game(session)
            if not game:
                # TODO: handle errors in middleware
                raise ValueError("Game not found")
            game.data = {
                "artist": artist,
            }
            game.state = TRANSITION_MAP[game.state]
            session.add(game)
            session.commit()


class SearchArtistState(rx.State):
    artists: list[ArtistDto] = []

    def search(self, query):
        logger.info(f"Searching for artists with query {query}")
        if len(query) < 1:
            logger.info("Query too short")
            self.artists = []
            return

        # TODO: rx.background
        client = SpotifyClient()
        self.artists = [
            ArtistDto(
                id=artist.id,
                name=artist.name,
                image_url=smallest_image(artist.images).url,
                genres=artist.genres,
            ) for artist in client.search_artists(query).artists.items
        ]
