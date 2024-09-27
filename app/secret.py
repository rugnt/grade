from datetime import datetime, timedelta

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt

from app.config import settings


unauthorized_exception = HTTPException(
    detail="Пользователь не авторизирован", status_code=status.HTTP_401_UNAUTHORIZED
)


class HTTPBearerToken(HTTPBearer):
    async def __call__(self, request: Request) -> str:
        try:
            http_credentials = await super().__call__(request)
        except HTTPException as e:
            raise JWTError from e
        return http_credentials.credentials if http_credentials is not None else None

oauth2_scheme = HTTPBearerToken()


class TokenOperatorMixin:
    """Предназначем для модели pydantic (BaseModel)"""

    exp: datetime | None = None

    def get_token(self):
        """Генерирует jwt токен по схеме"""
        payload = self.model_dump()
        if self.exp is None:
            payload.update({"exp": datetime.utcnow() + timedelta(minutes=30)})
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def create_token(data: dict, expires_time: int):
        payload = data.copy()
        payload.update({"exp": datetime.utcnow() + timedelta(minutes=expires_time)})

        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @classmethod
    def get_payload_from_token(cls, token):
        try:
            return cls.model_validate(
                jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            )
        except JWTError:
            raise unauthorized_exception

    @classmethod
    def get_payload_from_token_or_none(cls, token):
        try:
            return cls.model_validate(
                jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            )
        except JWTError:
            return None
