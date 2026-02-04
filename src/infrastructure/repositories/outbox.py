from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.outbox import OutboxCreateDTO, OutboxEventDTO
from src.application.interfaces.repositories import OutboxEventsProtocol
from src.domain.value_objects.outbox_event_status import OutboxEventStatusEnum
from ..db.models.outbox import OutboxEventORM


class OutboxEvents(OutboxEventsProtocol):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, event: OutboxCreateDTO) -> OutboxEventDTO:
        """Создание события в outbox"""
        new_event = OutboxEventORM(
            event_type=event.event_type,
            payload=event.payload,
            status=OutboxEventStatusEnum.PENDING,
        )
        self._session.add(new_event)
        await self._session.flush()
        await self._session.refresh(new_event)
        return OutboxEventDTO.model_validate(new_event)

    async def get_pending_events(self, limit: int = 100) -> list[OutboxEventDTO]:
        """Получение необработанных событий"""
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
        """Изменение статуса событие на SENT"""
        stmt = (
            update(OutboxEventORM)
            .where(OutboxEventORM.id == event_id)
            .values(status=OutboxEventStatusEnum.SENT)
        )
        await self._session.execute(stmt)
