import reflex as rx

from tastify.domain.page import page
from tastify.domain.router import Router
from tastify.domain.spotify.state import SpotifyState
from tastify import db


@page(route=Router.REGISTER_SPOTIFY_PATH, on_load=SpotifyState.register)
def registration() -> rx.Component:
    return rx.vstack(
        rx.cond(
            SpotifyState.state == db.SpotifyConnectorState.DISCONNECTED,
            rx.heading("Registering with Spotify...", size="5"),
            rx.text("Connected to Spotify", color="green"),
        ),
        rx.spacer(),
        rx.cond(
            SpotifyState.state == db.SpotifyConnectorState.DISCONNECTED,
            rx.spinner(size="large"),
            rx.button("Go to home page", on_click=Router.to_home()),
        ),
        align="center",
        spacing="6",
        padding_x=["1.5em", "1.5em", "3em"],
    )