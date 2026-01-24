import contextlib
import dataclasses
import typing

from src.infrastructure.db import Database
from .repositories.orders import Orders


@dataclasses.dataclass
class Repository:
    orders: Orders


class UnitOfWork:
    def __init__(self, db: Database):
        self.db = db

    @contextlib.asynccontextmanager
    async def init(self) -> typing.AsyncGenerator[Repository, None]:
        await self.db.create_database()
        async with self.db.connection() as conn:
            try:
                yield Repository(orders=Orders(conn))
            except Exception as e:
                await conn.rollback()
                raise e
            else:
                await conn.commit()
