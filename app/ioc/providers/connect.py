from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.config import AntifraudConfig, PostgresConfig, TelegramConfig
from app.database.postgres.session import create_engine
from app.interactors.moneyIteractor import MoneyIteractor
from app.interactors.telegramIteractor import TelegramInteractor
from app.utils.db_uri import is_valid_postgres_uri


class PostgresProvider(Provider):
    scope = Scope.APP

    @provide
    async def create_db_engine(self, config: PostgresConfig) -> AsyncIterable[AsyncEngine]:
        DB_URI = config.POSTGRES_CONN.replace("postgresql://", "postgresql+asyncpg://")
        if not is_valid_postgres_uri(config.POSTGRES_CONN):
            host = config.POSTGRES_HOST
            port = config.POSTGRES_PORT
            username = config.POSTGRES_USERNAME
            password = config.POSTGRES_PASSWORD
            db_name = config.POSTGRES_DATABASE

            DB_URI = f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{db_name}"

        async for engine in create_engine(DB_URI=DB_URI):
            yield engine


class TelegramProvider(Provider):
    scope = Scope.APP

    @provide(scope=Scope.APP)
    def get_telegram_interactor(
        self,
        telegram_config: TelegramConfig
    ) -> TelegramInteractor:
        # Создаем без MoneyIteractor
        return TelegramInteractor(
            bot_token=telegram_config.bot_token,
            chat_ids=telegram_config.chat_ids
        )