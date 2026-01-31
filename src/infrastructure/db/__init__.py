import contextlib
import typing

from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


class Base(DeclarativeBase):
    pass


class Database:
    def __init__(self, db_url: str) -> None:
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif db_url.startswith("postgresql://") and "+asyncpg" not in db_url:
            db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        self.engine = create_async_engine(db_url, echo=True)
        self.session_factory: sessionmaker[AsyncSession] = sessionmaker(  # type: ignore
            bind=typing.cast(Engine, self.engine),
            autoflush=False,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    async def create_database(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @contextlib.asynccontextmanager
    async def connection(self) -> typing.AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            yield session
