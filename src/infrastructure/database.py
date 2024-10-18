from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.core.config import settings

engine = create_async_engine(settings.get_db_url())
metadata.bind = engine


async def create_tables():
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)


async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)
