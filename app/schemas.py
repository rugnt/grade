import datetime

from typing import Optional
from pydantic import BaseModel
from .secret import TokenOperatorMixin


class Payload(BaseModel, TokenOperatorMixin):
    user_id: str
    exp: Optional[datetime.datetime] = None


class Success(BaseModel):
    success: bool


class HTTPError(BaseModel):
    detail: str
