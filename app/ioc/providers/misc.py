from dishka import Provider, Scope, provide

from app.core.config import SecurityConfig
from app.core.security import Security


class SecurityProvider(Provider):
    scope = Scope.APP

    @provide
    def create_security_service(self, config: SecurityConfig) -> Security:
        return Security(config)