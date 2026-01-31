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
        print(f"\n[DEBUG] Starting execute for order: {order.idempotency_key}")

        async with self._uow() as uow:
            # 1. Проверка идемпотентности
            existing_order = await uow.orders.get_by_idempotency_key(
                order.idempotency_key
            )
            if existing_order:
                print(f"[DEBUG] Order already exists: {existing_order.id}")
                return OrderReadDTO.model_validate(existing_order)

            # 2. Проверка каталога
            print(f"[DEBUG] Checking catalog for item: {order.item_id}")
            item = await self._catalog_service.check_available_qty(
                item_id=order.item_id, quantity=order.quantity
            )
            if not item:
                print("[DEBUG] Catalog check failed: Not enough quantity")
                raise IsAvailableQtyError("Not enough quantity in catalog")

            total_amount = item.price * order.quantity
            print(f"[DEBUG] Total amount calculated: {total_amount}")

            # 3. Создание заказа в БД
            new_order_orm = await uow.orders.create(order, total_amount)
            print(f"[DEBUG] Order created in DB with ID: {new_order_orm.id}")

            # 4. Вызов платежного сервиса
            payment_data = PaymentCreateDTO(
                order_id=new_order_orm.id,
                amount=total_amount,
                idempotency_key=order.idempotency_key,
            )

            try:
                print("[DEBUG] Calling payment service...")
                await self._payment_service.create_payment(payment_data)
                print("[DEBUG] Payment service responded successfully")
            except PaymentCreationError as e:
                print(f"[DEBUG] Payment service FAILED: {e}")
                # Пытаемся отменить заказ
                await uow.orders.update_status_with_outbox(
                    new_order_orm.id, OrderStatusEnum.CANCELLED
                )
                print("[DEBUG] Order status updated to CANCELLED")
                # ВАЖНО: Если мы здесь не рейзим ошибку, код пойдет дальше к return

            print("[DEBUG] Exiting UOW context (Commit should happen here)")

        # 5. Финальная валидация
        print("[DEBUG] Validating final OrderReadDTO")
        try:
            result = OrderReadDTO.model_validate(new_order_orm)
            print("[DEBUG] Validation successful, returning result")
            return result
        except Exception as e:
            print(f"[DEBUG] VALIDATION ERROR in OrderReadDTO: {e}")
            raise
