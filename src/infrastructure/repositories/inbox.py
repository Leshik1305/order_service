from uuid import UUID

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import func, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.inbox import InboxCreateDTO, InboxReadDTO
from src.application.exceptions import DuplicateEventError
from src.application.interfaces.repositories import InboxEventsProtocol
from src.domain.value_objects.inbox_event_status import InboxEventStatusEnum
from src.infrastructure.db.models.inbox import InboxEventORM


class InboxEvents(InboxEventsProtocol):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, event: InboxCreateDTO) -> InboxReadDTO | None:
        """Создание события в inbox"""
        stmt = (
            insert(InboxEventORM)
            .values(
                {
                    "idempotency_key": event.event_id,
                    "event_type": event.event_type,
                    "payload": event.payload,
                    "status": InboxEventStatusEnum.PENDING,
                    "created_at": func.now(),
                }
            )
            .on_conflict_do_nothing(index_elements=["idempotency_key"])
            .returning(InboxEventORM)
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()

        if row is None:
            raise DuplicateEventError(f"Event {event.event_id} already processed")

        return self._construct(row)

    # async def get_by_key(self, key: UUID) -> InboxMessageORM | None:
    #     result = await self._session.execute(
    #         select(InboxMessageORM).filter_by(idempotency_key=key)
    #     )
    #     return result.scalar_one_or_none()

    # async def get_pending_events(self, limit: int = 100) -> list[InboxReadDTO]:
    #     """Получение необработанных событий"""
    #     stmt = (
    #         select(InboxMessageORM)
    #         .where(InboxMessageORM.status == InboxEventStatusEnum.PENDING)
    #         .order_by(InboxMessageORM.created_at)
    #         .limit(limit)
    #     )
    #     result = await self._session.execute(stmt)
    #     rows = result.fetchall()
    #     return [self._construct(row) for row in rows]

    async def mark_as_processed(self, key: UUID) -> None:
        """Пометить событие как обработанное"""
        stmt = (
            update(InboxEventORM)
            .where(InboxEventORM.idempotency_key == key)
            .values(
                status=InboxEventStatusEnum.PROCESSED,
                processed_at=func.now(),
            )
        )
        await self._session.execute(stmt)

    @staticmethod
    def _construct(row) -> InboxReadDTO:
        return InboxReadDTO(
            event_id=row.idempotency_key,
            event_type=row.event_type,
            payload=row.payload,
            status=row.status,
            created_at=row.created_at,
            processed_at=row.processed_at,
        )
