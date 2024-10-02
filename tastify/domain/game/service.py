import sqlmodel
from sqlmodel import select

from tastify import db
from tastify.core.misc import filter_player


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


game_service = GameService()