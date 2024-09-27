import json

from typing import Any

from pydantic import BaseModel, field_validator, model_validator


class BookSchema(BaseModel):
    title: str
    category_id: int
    description: str
    rating: int

    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value: Any) -> Any:  # noqa: ANN102, ANN401
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

    @field_validator('rating', mode='after')
    @classmethod
    def validator_rating(cls, rating):
        if 0 <= rating <= 10:
            return rating
        raise ValueError('Диапазон рейтинга должен быть от 1 до 10')


class BookItem(BaseModel):
    id: int
    title: str
    description: str
    rating: int
    category: str
    image_url: str
    detail_url: str


class BookOutputSchema(BaseModel):
    items: list[BookItem]

