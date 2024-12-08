import asyncio
import logging
from contextlib import contextmanager

import reflex as rx
import sqlmodel

from tastify import db
from tastify.core.integration.spotify.client import SpotifyClient
from tastify.core.misc import smallest_image, filter_player
from tastify.domain.common.state import BaseState
from tastify.domain.game.service import game_service
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
    image_url: str | None = None
    genres: list[str]


class TrackDto(rx.Base):
    id: str
    name: str
    album_image_url: str
    preview_url: str | None = None


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


class RoundDto(rx.Base):
    round: int
    artist: str
    track: str


class GameState(BaseState):
    game: GameDto = None
    game_state: db.GameState = db.GameState.NEW
    my_user_uid: str = None
    players: list[UserGameDto] = []
    is_proposer: bool = False
    is_dashboard: bool = False  # TODO: explicitly switch to dashboard
    round: RoundDto = None

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
            db_game = game_service.get_game(session, self.room_code)
            self.game = _map_game(db_game)
            self.game_state = self.game.state
            self.players = _map_players(game_service.get_players(session, db_game.id))

            self.my_user_uid = self.get_client_uid()
            player = filter_player(self.my_user_uid, self.players)
            current_proposer = game_service.get_current_proposer(self.game.round, self.players)
            self.is_proposer = player == current_proposer
            self.is_dashboard = self.my_user_uid == self.game.created_by
            current_round_data = db_game.data.get("rounds", {}).get(str(self.game.round), {})
            my_player_data = current_round_data.get("players", {}).get(self.my_user_uid, {})
            self.round = RoundDto(
                round=db_game.round,
                artist=current_round_data.get("artist", {}).get("name", ""),
                track=my_player_data.get("track", {}).get("name", ""),
            )

    def move_game_state(self):
        logger.info(f"Moving game state from {self.game_state} to {TRANSITION_MAP[self.game_state]}")
        with self.modify_game() as (_, game):
            game.state = TRANSITION_MAP[game.state]

    def finalize_round(self):
        with self.modify_game() as (_, game):
            logger.info(f"Finalizing round {game.round} for game {game.id}")
            game.round += 1
            game.state = TRANSITION_MAP[game.state]

    async def select_artist(self, artist):
        logger.info(f"Selected artist {artist['name']}")
        await self.load_state()
        self.validate_is_proposer()
        self.validate_state(db.GameState.PROPOSE)

        with self.modify_game() as (_, game):
            data = dict(game.data.copy() or {})
            rounds_data = data.setdefault("rounds", {})
            logger.info(f"Current round: {self.round.round}")
            current_round_data = rounds_data.setdefault(str(self.round.round), {})
            current_round_data["artist"] = artist
            game.data = data.copy()
            game.state = TRANSITION_MAP[game.state]

    async def guesser_skip_round(self):
        logger.info("dont_like_artist()")
        await self.load_state()
        self.validate_is_guesser()
        self.validate_state(db.GameState.GUESS)

        with self.modify_game() as (session, game):
            data = game.data.copy()
            rounds_data = data.setdefault("rounds", {})
            current_round_data = rounds_data.setdefault(str(self.round.round), {}) # TODO: model
            current_round_player_data = current_round_data.setdefault("players", {})
            current_round_player_data[self.my_user_uid] = {"skipped": True}
            game.data = data.copy()
            if len(current_round_player_data) == len(self.players) - 1: # minus proposer
                game_service.calculate_scores(session, game, self.round.round)
                game.state = TRANSITION_MAP[game.state]


    async def select_track(self, track):
        logger.info(f"Selected track {track['name']}")
        await self.load_state()
        self.validate_is_guesser()
        self.validate_state(db.GameState.GUESS)

        with self.modify_game() as (session, game):
            data = game.data.copy()
            rounds_data = data.setdefault("rounds", {})
            current_round_data = rounds_data.setdefault(str(self.round.round), {}) # TODO: model
            current_round_player_data = current_round_data.setdefault("players", {})
            current_round_player_data[self.my_user_uid] = {"track": track}
            game.data = data.copy()
            if len(current_round_player_data) == len(self.players) - 1: # minus proposer
                game_service.calculate_scores(session, game, self.round.round)
                game.state = TRANSITION_MAP[game.state]

    @contextmanager
    def modify_game(self) -> tuple[sqlmodel.Session, db.Game]:
        with rx.session() as session:
            # TODO: resolve data race
            game = game_service.get_game(session, self.room_code)
            if not game:
                # TODO: handle errors in middleware
                raise ValueError("Game not found")
            yield session, game
            session.add(game)
            session.commit()

    def validate_is_proposer(self):
        if not self.is_proposer:
            logger.info("This action is only for proposer")
            return

    def validate_is_guesser(self):
        if self.is_proposer or self.is_dashboard:
            logger.info("This action is only for guesser")
            return

    def validate_state(self, state):
        if self.game_state != state:
            raise ValueError(f"Not in {state} state")


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
        items = client.search_artists(query).artists.items
        artists = []
        for item in items:
            image = smallest_image(item.images)
            artist = ArtistDto(
                id=item.id,
                name=item.name,
                image_url=image.url if image else None,
                genres=item.genres,
            )
            artists.append(artist)
        self.artists = artists

class SearchArtistTracksState(rx.State):
    tracks: list[TrackDto] = []

    def search(self, query, artist_name):
        logger.info(f"Searching for artists with query {query}")
        if len(query) < 1:
            logger.info("Query too short")
            self.tracks = []
            return

        # TODO: rx.background
        client = SpotifyClient()
        self.tracks = []
        for item in client.search_artist_tracks(query, artist_name).tracks.items:
            image = smallest_image(item.album.images)
            track = TrackDto(
                id=item.id,
                name=item.name,
                album_image_url=image.url if image else None,
                preview_url=item.preview_url,
            )
            self.tracks.append(track)
