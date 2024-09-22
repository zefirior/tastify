import functools
from typing import Any

import reflex as rx

from tastify.components.navbar import navbar


def page(
    route: str | None = None,
    title: str | None = None,
    image: str | None = None,
    description: str | None = None,
    meta: list[Any] | None = None,
    script_tags: list[Any] | None = None,
    on_load: Any | list[Any] | None = None,
):
    def _wrapper(render_fn):
        @rx.page(
            route=route,
            title=title,
            image=image,
            description=description,
            meta=meta,
            script_tags=script_tags,
            on_load=on_load,
        )
        @functools.wraps(render_fn)
        def _wrapped():
            return rx.vstack(
                navbar(),
                rx.spacer(),
                render_fn(),
                width="100%",
                spacing="6",
                padding_x=["1.5em", "1.5em", "3em"],
            )
        return _wrapped
    return _wrapper
