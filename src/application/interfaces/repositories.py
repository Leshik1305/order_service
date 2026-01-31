from decimal import Decimal
from typing import Protocol
from uuid import UUID

from ..dtos.order import OrderCreateDTO


class OrdersProtocol(Protocol):
    async def check_idempotency_key(self, idempotency_key: UUID): ...

    async def create(self, order: OrderCreateDTO, amount: Decimal): ...

    async def update_status_with_outbox(self, order_id: UUID, status: str): ...

    async def get_by_id(self, order_id: UUID): ...


class OutboxEventsProtocol(Protocol):
    async def create(self, event): ...


class InboxEventsProtocol(Protocol):
    async def create(self, message): ...


class Repository(Protocol):
    orders: OrdersProtocol
    outbox: OutboxEventsProtocol
    inbox: InboxEventsProtocol
