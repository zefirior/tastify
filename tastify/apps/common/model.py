import reflex as rx

from sqlmodel import Field


class User(rx.Model, table=True):
    """User in a room."""
    uid: str = Field(primary_key=True)
