from typing import Protocol
from uuid import UUID

from ..dtos.order import OrderCreateDTO


class Orders(Protocol):
    async def check_idempotency_key(self, idempotency_key: UUID): ...

    async def create(self, order: OrderCreateDTO, key: UUID): ...

    async def update_status(self, order_id: UUID, status: str): ...

    async def get_by_id(self, order_id: UUID): ...


class Repository(Protocol):
    orders: Orders
