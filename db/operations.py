from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from config import settings

async_engine = create_async_engine(settings.DATABASE_URL)


async def get_db():
    async with AsyncSession(async_engine, expire_on_commit=False) as session:
        yield session
