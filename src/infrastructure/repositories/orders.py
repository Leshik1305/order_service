from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from application.dtos.order import OrderCreateDTO
from application.exceptions import IdempotencyConflictError
from domain.value_objects.order_status import OrderStatusEnum
from ..db.models import OrderORM


class Orders:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, order: OrderCreateDTO, amount: Decimal):
        new_order = OrderORM(
            item_id=order.item_id,
            quantity=order.quantity,
            amount=amount,
            idempotency_key=order.idempotency_key,
            status=OrderStatusEnum.NEW,
        )
        self.session.add(new_order)

        await self.session.flush()

        await self.session.refresh(new_order)

        return new_order

    async def check_idempotency_key(self, idempotency_key: UUID):
        stmt = await self.session.execute(
            select(OrderORM).where(OrderORM.idempotency_key == idempotency_key)
        )
        if stmt.scalar_one_or_none():
            raise IdempotencyConflictError("Such an order already exists!")

    async def update_status(self, order_id: UUID, status: str) -> None:
        query = update(OrderORM).where(OrderORM.id == order_id).values(status=status)
        await self.session.execute(query)

    async def get_by_id(self, order_id: UUID) -> Optional[OrderORM]:
        query = select(OrderORM).where(OrderORM.id == order_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
