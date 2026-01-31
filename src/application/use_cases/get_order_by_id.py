from uuid import UUID

from ..dtos.order import OrderReadDTO
from ..exceptions import OrderNotFoundError
from ..interfaces.uow import UnitOfWork


class GetOrderByIdUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
    ):
        self._uow = uow

    async def get_order(self, order_id: UUID) -> OrderReadDTO:
        async with self._uow() as uow:
            order = await uow.orders.get_by_id(order_id)
            if not order:
                raise OrderNotFoundError(f"Order with id {order_id} not found")
            return OrderReadDTO.model_validate(order)
