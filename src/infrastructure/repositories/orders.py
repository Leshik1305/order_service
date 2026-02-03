from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4, uuid5, NAMESPACE_DNS

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.outbox import OutboxCreateDTO
from src.application.dtos.order import OrderCreateDTO
from src.application.exceptions import IdempotencyConflictError
from src.domain.value_objects.order_status import OrderStatusEnum
from .outbox import OutboxEvents
from ..db.models.orders import OrderORM

from ...application.interfaces.repositories import OrdersProtocol
from ...domain.value_objects.event_type import EventTypeEnum


class Orders(OrdersProtocol):
    def __init__(self, session: AsyncSession, outbox: OutboxEvents):
        self._session = session
        self._outbox = outbox

    async def _create_outbox_event(self, order: OrderORM, event_suffix: str) -> None:
        event_type = f"order.{event_suffix.lower()}"
        idempotency_key = uuid5(NAMESPACE_DNS, f"{order.id}:{event_type}")

        payload = {
            "event_type": event_type,
            "order_id": str(order.id),
            "item_id": str(order.item_id),
            "quantity": order.quantity,
            "idempotency_key": str(idempotency_key),
        }
        event_dto = OutboxCreateDTO(
            event_type=EventTypeEnum(event_type),
            payload=payload,
        )
        await self._outbox.create(event=event_dto)

    async def create(self, order: OrderCreateDTO, amount: Decimal) -> OrderORM:
        new_order = OrderORM(
            item_id=order.item_id,
            user_id=order.user_id,
            quantity=order.quantity,
            amount=amount,
            idempotency_key=order.idempotency_key,
            status=OrderStatusEnum.NEW,
        )
        self._session.add(new_order)

        await self._session.flush()

        await self._session.refresh(new_order)

        await self._create_outbox_event(new_order, "created")

        return new_order

    async def get_by_idempotency_key(self, idempotency_key: str) -> Optional[OrderORM]:
        stmt = select(OrderORM).where(OrderORM.idempotency_key == idempotency_key)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_status_with_outbox(
        self, order_id: UUID, status: OrderStatusEnum
    ) -> None:
        stmt = (
            update(OrderORM)
            .where(OrderORM.id == order_id)
            .values(status=status)
            .returning(OrderORM)
        )
        result = await self._session.execute(stmt)
        order = result.scalar_one_or_none()
        if order:
            await self._create_outbox_event(order, status.value)

    async def update_status(self, order_id: UUID, status: OrderStatusEnum) -> None:
        stmt = update(OrderORM).where(OrderORM.id == order_id).values(status=status)
        await self._session.execute(stmt)

    async def get_by_id(self, order_id: UUID) -> Optional[OrderORM]:
        query = select(OrderORM).where(OrderORM.id == order_id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()
