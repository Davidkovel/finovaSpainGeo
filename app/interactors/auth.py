from typing import Dict

from app.core.exceptions import (
    EmailAlreadyExistsError,
    EntityUnauthorizedError,
    InvalidCredentialsError,
)
from app.core.security import Security
from app.database.repositories.user import UserRepository
from app.schemas.user import UserLogin, UserRegister


class SignUpUserInteractor:
    def __init__(self, user_repository: UserRepository, security: Security):
        self.user_repository = user_repository
        self.security = security

    async def __call__(self, user_register: UserRegister) -> str:
        exist_user = await self.user_repository.get_user_by_email(user_register.email)
        if exist_user:
            raise EmailAlreadyExistsError

        new_user = await self.user_repository.create_new_user(user_register, self.security)

        # Создаём JWT-токен, включая ID и email
        token_data = {
            "sub": str(new_user.id),
            "email": new_user.email
        }
        token = self.security.create_access_token(token_data)

        return token


class SignInUserInteractor:
    def __init__(self, user_repository: UserRepository, security: Security):
        self.user_repository = user_repository
        self.security = security

    async def __call__(self, user_login: UserLogin) -> str:
        user = await self.user_repository.get_user_by_email(user_login.email)
        if not user:
            raise InvalidCredentialsError

        if not self.security.verify_password(user_login.password, user.password):
            raise InvalidCredentialsError

        token_data = {
            "sub": str(user.id),
            "email": user.email
        }
        token = self.security.create_access_token(token_data)

        return token


class OAuth2PasswordBearerUserInteractor:
    def __init__(self, security: Security):
        self.security = security

    async def __call__(self, token: str) -> Dict[str, str]:
        """Returning user id"""

        decoded_token = self.security.decode_access_token(token)
        if not decoded_token:
            raise EntityUnauthorizedError

        user_id = decoded_token.get("sub")
        email = decoded_token.get("email")

        if not user_id or not email:
            raise EntityUnauthorizedError

        return {"user_id": user_id, "email": email}
