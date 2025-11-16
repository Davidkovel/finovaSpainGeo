from dishka import Provider, Scope, from_context, provide

from app.core.config import (
    Config,
    PostgresConfig,
    SecurityConfig,
    create_config, TelegramConfig,
)


class ConfigProvider(Provider):
    scope = Scope.APP
    config = from_context(provides=Config)

    @provide
    def get_config(self) -> Config:
        return create_config()

    @provide
    def get_postgres_config(self, config: Config) -> PostgresConfig:
        return config.postgres_config

    @provide
    def get_auth_token_config(self, config: Config) -> SecurityConfig:
        return config.auth_token_config

    @provide
    def get_telegram_config(self, config: Config) -> TelegramConfig:
        return config.telegram_config
