import asyncio

from sqlalchemy import insert

from app.database import async_session_maker
from app.models import Category


async def add_books():
    async with async_session_maker() as db:
        result_from_db = await db.execute(
            insert(Category).values([
                {'title': 'Фантастика'},
                {'title': 'Романы'}
            ]).returning(Category.id)
        )
        categories_id = list(result_from_db.scalars())
        await db.commit()


asyncio.run(add_books())
