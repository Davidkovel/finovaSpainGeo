from collections.abc import AsyncIterable

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from app.database.postgres.base import Base


async def create_engine(DB_URI: str) -> AsyncIterable[AsyncSession]:
    engine = create_async_engine(url=DB_URI, echo=False, future=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


async def create_all_tables(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db(engine: AsyncEngine) -> AsyncIterable[AsyncSession]:
    async with AsyncSession(bind=engine, expire_on_commit=False) as db_session:
        yield db_session
