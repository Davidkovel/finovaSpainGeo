import uuid
from datetime import datetime, timedelta
from typing import Optional

from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from app.core.config import SecurityConfig


class Security:
    def __init__(self, config: SecurityConfig):
        self.config = config

        self.pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.config.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update(iat=datetime.utcnow(), exp=expire, jti=str(uuid.uuid4()))

        return jwt.encode(claims=to_encode, key=self.config.RANDOM_SECRET, algorithm=self.config.ALGORITH)

    def decode_access_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.config.RANDOM_SECRET, algorithms=[self.config.ALGORITH])
            return payload
        except (JWTError, ExpiredSignatureError):
            return None