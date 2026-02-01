from typing import Optional

from sqlalchemy import insert, literal_column, update, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.outbox import OutboxCreateDTO, OutboxEventDTO

from src.infrastructure.db.models.outbox import OutboxEventORM

from src.domain.value_objects.outbox_event_status import OutboxEventStatusEnum
from src.application.interfaces.repositories import OutboxEventsProtocol


class OutboxEvents(OutboxEventsProtocol):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, event: OutboxCreateDTO) -> OutboxEventDTO:
        stmt = (
            insert(OutboxEventORM)
            .values(
                {
                    "event_type": event.event_type,
                    "payload": event.payload,
                }
            )
            .returning(literal_column("*"))
        )
        result = await self._session.execute(stmt)
        row = result.fetchone()
        return self._construct(row)

    async def get_pending_events(self, limit: int = 100) -> list[OutboxEventDTO]:
        stmt = (
            select(OutboxEventORM)
            .where(OutboxEventORM.status == OutboxEventStatusEnum.PENDING)
            .order_by(OutboxEventORM.created_at)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        events = result.scalars().all()
        return [OutboxEventDTO.model_validate(event) for event in events]

    async def mark_as_sent(self, event_id: str) -> None:
        stmt = (
            update(OutboxEventORM)
            .where(OutboxEventORM.id == event_id)
            .values(status=OutboxEventStatusEnum.SENT)
        )
        await self._session.execute(stmt)

    @staticmethod
    def _construct(row) -> Optional[OutboxEventDTO]:

        if row is None:
            return None

        return OutboxEventDTO(
            id=row.id,
            event_type=row.event_type,
            payload=row.payload,
            status=OutboxEventStatusEnum(row.status),
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
