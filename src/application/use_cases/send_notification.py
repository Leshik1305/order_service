import logging

from src.infrastructure.http.notifications_service import NotificationsServiceAPI

logger = logging.getLogger(__name__)


class SendNotificationUseCase:
    def __init__(self, notifications_api: NotificationsServiceAPI):
        self._notifications_api = notifications_api
        self._templates = {
            "order.created": "NEW: Ваш заказ создан и ожидает оплаты",
            "order.paid": "PAID: Ваш заказ успешно оплачен и готов к отправке",
            "order.shipped": "SHIPPED: Ваш заказ отправлен в доставку.",
            "order.cancelled": "CANCELLED: Ваш заказ отменен.",
        }

    async def execute(self, event_payload: dict, event_type: str) -> None:

        if event_type not in self._templates:
            logger.warning(f"Unknown event type: {event_type}")
            return
        message = self._templates.get(event_type)
        idempotency_key = event_payload.get("idempotency_key")
        order_id = event_payload.get("order_id")
        if not order_id:
            logger.error(f"Missing order_id in event_payload for event {event_type}")
            return
        try:
            print("UP")
            response_data = await self._notifications_api.send_notification(
                message=message,
                idempotency_key=idempotency_key,
                order_id=order_id,
            )
            for i in range(10):
                logger.info(
                    f"SUCCESS: Сервис уведомлений ответил. Данные: {response_data}"
                )
        except Exception as e:
            logger.error(f"Failed to send notification for {event_type}: {e}")
