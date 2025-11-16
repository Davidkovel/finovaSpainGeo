from collections.abc import Iterable

from dishka import AsyncContainer, Provider, make_async_container

from app.core.config import Config, create_config


def create_async_container(providers: Iterable[Provider]) -> AsyncContainer:
    config = create_config()
    return make_async_container(*providers, context={Config: config})