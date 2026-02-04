from src.domain.value_objects.order_status import OrderStatusEnum
from src.infrastructure.uow import UnitOfWork

from ..dtos.payment import PaymentCallbackDTO
from ..exceptions import OrderNotFoundError


class PaymentCallback:
    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    async def execute(self, callback_data: PaymentCallbackDTO) -> None:
        async with self._uow() as uow:
            order = await uow.orders.get_by_id(callback_data.order_id)
            if not order:
                raise OrderNotFoundError("Order not found")
            if order.status in [OrderStatusEnum.PAID, OrderStatusEnum.CANCELLED]:
                return
            new_status = (
                OrderStatusEnum.PAID
                if callback_data.status == "succeeded"
                else OrderStatusEnum.CANCELLED
            )
            await uow.orders.update_status_with_outbox(order.id, new_status)
