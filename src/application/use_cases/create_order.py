from src.domain.value_objects.order_status import OrderStatusEnum
from ..dtos.order import OrderCreateDTO, OrderReadDTO
from ..dtos.payment import PaymentCreateDTO
from ..exceptions import (
    IsAvailableQtyError,
    PaymentCreationError,
)

from ..interfaces.uow import UnitOfWork
from src.infrastructure.http.catalog_service import CatalogServiceAPI
from src.infrastructure.http.payments_service import PaymentsServiceAPI


class CreateOrder:
    def __init__(
        self,
        uow: UnitOfWork,
        catalog: CatalogServiceAPI,
        payment: PaymentsServiceAPI,
    ):
        self._uow = uow
        self._catalog_service = catalog
        self._payment_service = payment

    async def execute(self, order: OrderCreateDTO) -> OrderReadDTO:

        async with self._uow() as uow:

            await uow.orders.check_idempotency_key(order.idempotency_key)

            item = await self._catalog_service.check_available_qty(
                item_id=order.item_id, quantity=order.quantity
            )
            if not item:
                raise IsAvailableQtyError("Not enough quantity in catalog")
            total_amount = item.price * order.quantity

            new_order_orm = await uow.orders.create(order, total_amount)

            payment_data = PaymentCreateDTO(
                order_id=new_order_orm.id,
                amount=total_amount,
                idempotency_key=order.idempotency_key,
            )
            try:
                await self._payment_service.create_payment(payment_data)
            except PaymentCreationError:
                await uow.orders.update_status_with_outbox(
                    new_order_orm.id, OrderStatusEnum.CANCELLED
                )
            finally:
                return OrderReadDTO.model_validate(new_order_orm)
