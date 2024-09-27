from pydantic import BaseModel, EmailStr, model_validator


class Registration(BaseModel):
    email: EmailStr
    password1: str
    password2: str

    @model_validator(mode='before')
    def check_passwords_match(cls, values):
        pw1, pw2 = values.get('password1'), values.get('password2')
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError('Пароли не совпадают')
        return values


class Tokens(BaseModel):
    access_token: str
    refresh_token: str
