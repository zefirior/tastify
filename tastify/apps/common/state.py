import uuid

import reflex as rx
from sqlmodel import select

from tastify.db.user import User


class CommonState(rx.State):
    user_name: str = ""
    client_uid: str = rx.LocalStorage(name="client_uid")

    def get_client_uid(self) -> str:
        if not self.client_uid:
            self.client_uid = str(uuid.uuid4())
        return self.client_uid

    def get_or_create_user(self, session):
        user = session.exec(select(User).where(User.uid == self.get_client_uid())).first()
        if not user:
            user = User(uid=self.get_client_uid())
            session.add(user)
            session.commit()
        return user
