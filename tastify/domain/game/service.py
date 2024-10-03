from math import ceil

import sqlmodel
from sqlmodel import select

from tastify import db
from tastify.core.misc import filter_player

GUESSER_SCORE_DIFF = 1
PROPOSER_SCORE_DIFF_PER_GUESSER = 1
PROPOSER_SCORE_DIFF = 1
FAIL_PROPOSER_SCORE_DIFF = -1


class GameService:
    # def __init__(self):
    #     self.games = []

    def get_game(self, session: sqlmodel.Session, room_code: str) -> db.Game:
        game = session.exec(
            select(db.Game).join(
                db.Room, db.Room.id == db.Game.room_id,
            ).order_by(
                db.Game.created_at,
            ).where(
                db.Room.code == room_code,
            )
        ).first()
        if not game:
            # TODO: handle errors in middleware
            raise ValueError("Game not found")
        return game

    def guesser_skip_round(self, session: sqlmodel.Session, room_code: str, user_uid: str) -> db.Game:
        game = self.get_game(session, room_code)
        players = self.get_players(session, game.id)
        player = filter_player(user_uid, players)

        game = session.exec(
            select(db.Game).join(
                db.Room, db.Room.id == db.Game.room_id,
            ).order_by(
                db.Game.created_at,
            ).where(
                db.Room.code == room_code,
            )
        ).first()
        if not game:
            raise ValueError("Game not found")
        return game

    def get_players(self, session: sqlmodel.Session, game_id: int) -> list[db.UserGame]:
        return list(session.exec(
            select(
                db.UserGame
            ).join(
                db.Game,
                db.Game.id == db.UserGame.game_id
            ).where(db.Game.id == game_id)
        ).all())

    def calculate_scores(self, session: sqlmodel.Session, game: db.Game, round: int):
        data = game.data
        rounds_data = data["rounds"][str(round)]

        players = self.get_players(session, game.id)
        proposer = self.get_current_proposer(game.round, players)
        guessers = [player for player in players if player != proposer]

        count_winners = 0
        for guesser in guessers:
            player_data = rounds_data["players"][guesser.user_uid]
            if player_data.get("skipped", False):
                continue
            count_winners += 1
            guesser.score += GUESSER_SCORE_DIFF

        if count_winners == 0:
            proposer.score += FAIL_PROPOSER_SCORE_DIFF
        elif count_winners <= ceil(len(guessers) / 2):
            proposer.score += (count_winners * PROPOSER_SCORE_DIFF_PER_GUESSER + PROPOSER_SCORE_DIFF)

        session.add(proposer)
        session.add_all(guessers)

    @staticmethod
    def get_current_proposer(round: int, players: list[db.UserGame]) -> db.UserGame:
        current_player_index = round % len(players)
        return sorted(
            players,
            key=lambda player: player.user_uid,
        )[current_player_index]


game_service = GameService()