import hashlib
import os

from alembic.util import status
from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import Tokens
from app.models import Token, User
from app.schemas import Payload


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_access_and_refresh_token(user_id: str, db: AsyncSession):
    new_refresh_token = hashlib.sha256(os.urandom(32)).hexdigest()
    query = (
        insert(Token)
        .values({'id': new_refresh_token, 'user_id': user_id})
        .on_conflict_do_nothing(index_elements=['id'])
        .returning(Token.id)
    )
    result_from_db = await db.execute(query)
    token = result_from_db.scalar_one()
    await db.commit()
    if token:
        payload = Payload(user_id=user_id)
        return Tokens(
            access_token=payload.get_token(),
            refresh_token=new_refresh_token
        )
    return create_access_and_refresh_token(user_id, db)


async def refresh(db: AsyncSession, refresh_token: str):
    result_from_db = await db.execute(select(Token.user_id).select_from(Token).where(Token.id == refresh_token))
    user_id = result_from_db.scalar_one_or_none()
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Bad Request')

    return Tokens(
        access_token=Payload(user_id=user_id).get_token(),
        refresh_token=refresh_token
    )


async def login_user(db: AsyncSession, email: str, password: str):
    query = select(User).where(User.email == email)
    result_from_db = await db.execute(query)
    user = result_from_db.scalar_one_or_none()

    if user is not None and pwd_context.verify(password, user.hashed_password):
        return await create_access_and_refresh_token(user.id, db)

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Не правильный логин или пароль')


async def logout_user(db: AsyncSession, refresh_token: str):
    query = delete(Token).where(Token.id == refresh_token).returning(Token.id)

    result_from_db = await db.execute(query)

    if result_from_db.scalar_one_or_none():
        await db.commit()
        return {'success': True}

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Bad Request')


async def registration_user(db: AsyncSession, email: str, password: str):
    hashed_password = pwd_context.hash(password)
    insert_stmt = insert(User).values({
        'email': email,
        'hashed_password': hashed_password
    })
    do_nothing_stmt = insert_stmt.on_conflict_do_nothing(index_elements=['email']).returning(User.id)
    result_from_db = await db.execute(do_nothing_stmt)
    user_id = result_from_db.scalar_one_or_none()
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Такой пользователь уже существует'
        )

    result = await create_access_and_refresh_token(
        user_id=user_id,
        db=db
    )
    await db.commit()
    return result



