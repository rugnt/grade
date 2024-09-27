from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine
from typing import Generator
from .config import settings


async_engine = create_async_engine(settings.ASYNC_DATABASE_URL)
sync_engine = create_engine(settings.SYNC_DATABASE_URL)

async_session_maker = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
sync_session_maker = sessionmaker(sync_engine, expire_on_commit=False)


async def get_db() -> Generator:
    """Dependency for getting async session"""
    try:
        session: AsyncSession = async_session_maker()
        yield session
    finally:
        await session.close()


class Base(DeclarativeBase):
    pass
