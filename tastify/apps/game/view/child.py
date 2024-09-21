import abc

import reflex as rx


class ChildRenderer(abc.ABC):
    @abc.abstractmethod
    def render_new(self) -> rx.Component:
        pass

    @abc.abstractmethod
    def render_preparing(self) -> rx.Component:
        pass

    @abc.abstractmethod
    def render_propose(self) -> rx.Component:
        pass

    @abc.abstractmethod
    def render_guess(self) -> rx.Component:
        pass

    @abc.abstractmethod
    def render_result(self) -> rx.Component:
        pass
