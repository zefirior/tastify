import reflex as rx

from tastify.apps import index
from tastify.core.log import configure_logging

configure_logging()

app = rx.App(
    theme=rx.theme(
        appearance="dark", has_background=True, radius="large", accent_color="grass"
    ),
)

app.add_page(
    index,
    title="Tastify",
    description="Game for exploring friend's music tastes",
)
