import logging

from src.domain.value_objects.order_status import OrderStatusEnum
from src.infrastructure.http.catalog_service import CatalogServiceAPI
from src.infrastructure.http.payments_service import PaymentsServiceAPI

from ..dtos.order import OrderCreateDTO, OrderReadDTO
from ..dtos.payment import PaymentCreateDTO
from ..exceptions import (
    IsAvailableQtyError,
    PaymentCreationError,
)
from ..interfaces.uow import UnitOfWork

logger = logging.getLogger(__name__)


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
        logger.info(
            f">>> Starting CreateOrder. Idempotency key: {order.idempotency_key}"
        )
        async with self._uow() as uow:
            existing_order = await uow.orders.get_by_idempotency_key(
                order.idempotency_key
            )
            if existing_order:
                logger.info(
                    f"Order already exists: {order.idempotency_key}. Returning existing."
                )
                return OrderReadDTO.model_validate(existing_order)

            item = await self._catalog_service.check_available_qty(
                item_id=order.item_id, quantity=order.quantity
            )
            if not item:
                logger.error(f"Availability check failed for item {order.item_id}")
                raise IsAvailableQtyError("Not enough quantity in catalog")
            total_amount = item.price * order.quantity

            new_order_orm = await uow.orders.create(order, total_amount)
            logger.info(f"Order created in DB with ID: {new_order_orm.id}")
            payment_data = PaymentCreateDTO(
                order_id=new_order_orm.id,
                amount=total_amount,
                idempotency_key=order.idempotency_key,
            )
            try:
                logger.info(f"Calling payment service for order {new_order_orm.id}")
                await self._payment_service.create_payment(payment_data)
                logger.info("Payment service responded successfully")
            except PaymentCreationError as e:
                logger.warning(
                    f"Payment failed: {str(e)}. Cancelling order {new_order_orm.id}"
                )
                await uow.orders.update_status_with_outbox(
                    new_order_orm.id, OrderStatusEnum.CANCELLED
                )
            except Exception as e:
                logger.error(
                    f"Unexpected error during payment: {type(e).__name__}: {e}"
                )
                raise
            logger.info(
                f"UoW block finished for order {new_order_orm.id}. Committing..."
            )
        logger.info(
            f"<<< CreateOrder finished successfully. Order ID: {new_order_orm.id}"
        )
        return OrderReadDTO.model_validate(new_order_orm)
