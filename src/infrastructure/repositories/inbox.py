from uuid import UUID

from sqlalchemy import func, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.inbox import InboxCreateDTO, InboxReadDTO
from src.application.exceptions import DuplicateEventError
from src.application.interfaces.repositories import InboxEventsProtocol
from src.domain.value_objects.inbox_event_status import InboxEventStatusEnum
from ..db.models.inbox import InboxEventORM


class InboxEvents(InboxEventsProtocol):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, event: InboxCreateDTO) -> InboxReadDTO | None:
        """Создание события в inbox"""
        stmt = (
            insert(InboxEventORM)
            .values(
                {
                    "idempotency_key": event.idempotency_key,
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
            raise DuplicateEventError(
                f"Event {event.idempotency_key} already processed"
            )

        return self._construct(row)

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
            idempotency_key=row.idempotency_key,
            event_type=row.event_type,
            payload=row.payload,
            status=row.status,
            created_at=row.created_at,
            processed_at=row.processed_at,
        )
