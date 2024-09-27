import datetime

from pydantic import BaseModel

from .secret import TokenOperatorMixin


class Payload(BaseModel, TokenOperatorMixin):
    user_id: str
    exp: datetime.datetime | None = None


class Success(BaseModel):
    success: bool


class HTTPError(BaseModel):
    detail: str
