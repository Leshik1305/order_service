from uuid import NAMESPACE_DNS, uuid5, UUID

from ..dtos.inbox import InboxCreateDTO
from ..exceptions import DuplicateEventError, ProcessInboxError
from ..interfaces.uow import UnitOfWork
from ...domain.value_objects.order_status import OrderStatusEnum


class ProcessInboxEventsUseCase:
    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    async def execute(self, payload: dict):
        event_type_value = payload.get("event_type")
        order_id_str = payload.get("order_id")
        if not event_type_value or not order_id_str:
            raise Exception(f"Invalid payload received: {payload}")
        idempotency_key = uuid5(NAMESPACE_DNS, f"{order_id_str}:{event_type_value}")

        try:
            async with self._uow() as uow:
                try:
                    await uow.inbox.create(
                        InboxCreateDTO(
                            idempotency_key=idempotency_key,
                            event_type=event_type_value,
                            payload=payload,
                        )
                    )
                except DuplicateEventError:
                    return

                if event_type_value == "order.shipped":
                    await uow.orders.update_status_with_outbox(
                        UUID(order_id_str), OrderStatusEnum.SHIPPED
                    )
                elif event_type_value == "order.cancelled":
                    await uow.orders.update_status_with_outbox(
                        UUID(order_id_str), OrderStatusEnum.CANCELLED
                    )
                else:
                    raise ValueError(f"Unsupported event {event_type_value}")

                await uow.inbox.mark_as_processed(idempotency_key)

        except Exception as e:
            raise ProcessInboxError(f"Failed to process event {idempotency_key}: {e}")
