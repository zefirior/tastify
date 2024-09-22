import reflex as rx

from tastify.domain.page import page
from tastify.domain.room.state import RoomState, JoinRoomState
from tastify.domain.router import Router


@page(route=Router.ROOM_PATH, on_load=RoomState.refresh_room)
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
        rx.hstack(
            rx.cond(
                RoomState.is_dashboard,
                rx.button(
                    "Start game",
                    on_click=RoomState.start_game,
                    disabled=~RoomState.is_enough_players,
                ),
                rx.spacer(),
            ),
            rx.image(src=RoomState.room_qrcode, width="100%"),
            rx.button(
                "Join room (DEV)",
                on_click=RoomState.join_room_redirect,
                color="green",
            ),
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


@page(route=Router.JOIN_ROOM_PATH)
def join() -> rx.Component:
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
        rx.hstack(
            rx.input(
                placeholder="Your name",
                value=JoinRoomState.user_name,
                on_change=JoinRoomState.set_user_name,
                width="100%",
                margin_bottom="4",
            ),
            rx.button("Join", on_click=JoinRoomState.join_room),
        ),
        rx.heading("Users in room", size="5"),
        width="100%",
        spacing="6",
        padding_x=["1.5em", "1.5em", "3em"],
        on_mount=RoomState.load_room,
    )
