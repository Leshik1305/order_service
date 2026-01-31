from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .repositories.inbox import InboxEvents
from .repositories.orders import Orders
from .repositories.outbox import OutboxEvents


class _UnitOfWorkImplementation:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._outbox_repo = OutboxEvents(session)
        self._order_repo = Orders(session, outbox=self._outbox_repo)
        self._inbox_repo = InboxEvents(session)

    @property
    def orders(self) -> Orders:
        return self._order_repo

    @property
    def outbox(self) -> OutboxEvents:
        return self._outbox_repo

    @property
    def inbox(self) -> InboxEvents:
        return self._inbox_repo

    async def commit(self):
        await self._session.commit()


class UnitOfWork:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    @asynccontextmanager
    async def __call__(self):
        async with self._session_factory() as session:
            uow_impl = _UnitOfWorkImplementation(session)
            try:
                yield uow_impl
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
