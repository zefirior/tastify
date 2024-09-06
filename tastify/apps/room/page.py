import reflex as rx

from tastify.apps.room.state import RoomState
from tastify.apps.router import Router


@rx.page(route=Router.ROOM_PATH, on_load=RoomState.refresh_room)
def room() -> rx.Component:
    return rx.vstack(
        rx.badge(
            rx.icon(tag="table-2", size=28),
            rx.heading(f"Room {RoomState.room_code}", size="6"),
            color_scheme="green",
            radius="large",
            align="center",
            variant="surface",
            padding="0.65rem",
        ),
        rx.spacer(),
        rx.heading("Users in room", size="5"),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("UID"),
                    rx.table.column_header_cell("Name"),
                ),
            ),
            rx.table.body(
                rx.foreach(
                    RoomState.users_in_room,
                    lambda user: rx.table.row(
                        rx.table.row_header_cell(user.user_uid),
                        rx.table.cell(user.name),
                    ),
                )
            ),
            width="100%",
        ),
        width="100%",
        spacing="6",
        padding_x=["1.5em", "1.5em", "3em"],
        on_mount=RoomState.load_room,
    )
