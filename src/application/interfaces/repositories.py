from decimal import Decimal
from typing import Protocol, List
from uuid import UUID

from ..dtos.order import OrderCreateDTO
from ...domain.value_objects.order_status import OrderStatusEnum
from ...infrastructure.db.models import OrderORM


class OrdersProtocol(Protocol):
    async def check_idempotency_key(self, idempotency_key: UUID): ...

    async def create(self, order: OrderCreateDTO, amount: Decimal): ...

    async def get_by_id(self, order_id: UUID): ...

    async def _create_outbox_event(self, order: OrderORM, event_suffix: str): ...

    async def update_status_with_outbox(
        self, order_id: UUID, status: OrderStatusEnum
    ): ...


class OutboxEventsProtocol(Protocol):
    async def create(self, event): ...

    async def get_pending_events(self, limit: int = 100): ...

    async def mark_as_sent(self, event_id: UUID): ...


class InboxEventsProtocol(Protocol):
    async def create(self, message): ...

    async def mark_as_processed(self, key: UUID): ...


class Repository(Protocol):
    orders: OrdersProtocol
    outbox: OutboxEventsProtocol
    inbox: InboxEventsProtocol
