from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import get_settings

settings = get_settings()

engine = None
async_session = None


def _init_engine():
    global engine, async_session
    if engine is None:
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_engine():
    _init_engine()
    return engine


def get_session_factory():
    _init_engine()
    return async_session


async def get_db():
    _init_engine()
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
