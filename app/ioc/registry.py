from collections.abc import Iterable

from dishka import Provider

from app.ioc.providers import (
    RepositoryProvider,
    PostgresProvider,
    InteractorProvider,
    ConfigProvider,
    SecurityProvider
)
from app.ioc.providers.connect import TelegramProvider


def get_providers() -> Iterable[Provider]:
    return (
        RepositoryProvider(),
        PostgresProvider(),
        InteractorProvider(),
        ConfigProvider(),
        SecurityProvider(),
        TelegramProvider()
    )
