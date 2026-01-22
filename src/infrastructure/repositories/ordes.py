from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.order import OrderCreateDTO
from src.application.exceptions import IdempotencyConflictError
from src.domain.value_objects.order_status import OrderStatusEnum
from src.infrastructure.db.models import OrderORM


class Orders:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, order: OrderCreateDTO):
        new_order = OrderORM(
            item_id=order.item_id,
            quantity=order.quantity,
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
