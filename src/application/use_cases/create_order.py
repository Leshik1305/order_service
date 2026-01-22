from uuid import uuid4

from src.application.dtos.order import OrderCreateDTO, OrderReadDTO
from src.application.exceptions import IsAvailableQtyError, IdempotencyConflictError

from src.application.interfaces.uow import UnitOfWork
from src.infrastructure.http.http_clients import CatalogServiceAPI


class CreateOrder:
    def __init__(self, uow: UnitOfWork, catalog: CatalogServiceAPI):
        self._uow = uow
        self._catalog = catalog

    async def execute(self, order: OrderCreateDTO) -> OrderReadDTO:

        async with self._uow.init() as repo:

            result = await repo.orders.check_idempotency_key(order.idempotency_key)
            if result:
                raise IdempotencyConflictError
            is_available = await self._catalog.check_available_qty(
                item_id=order.item_id, quantity=order.quantity
            )
            if is_available:
                new_order_orm = await repo.orders.create(order)
                return OrderReadDTO.model_validate(new_order_orm)
            else:
                raise IsAvailableQtyError
