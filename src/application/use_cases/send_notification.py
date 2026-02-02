import logging

from src.infrastructure.http.notifications_service import NotificationsServiceAPI

logger = logging.getLogger(__name__)


class SendNotificationUseCase:
    def __init__(self, notifications_api: NotificationsServiceAPI):
        self._notifications_api = notifications_api
        self._templates = {
            "order.new": "Ваш заказ создан и ожидает оплаты",
            "order.paid": "Ваш заказ успешно оплачен и готов к отправке",
            "order.shipped": "Ваш заказ отправлен в доставку",
            "order.cancelled": "Ваш заказ отменен.",
        }

    async def execute(self, event_payload: dict) -> None:
        event_type = event_payload.get("event_type")
        if event_type not in self._templates:
            return
        message = self._templates.get(event_type)
        idempotency_key = event_payload.get("idempotency_key")
        try:
            await self._notifications_api.send_notification(
                message=message, idempotency_key=idempotency_key
            )
        except Exception as e:
            logger.error(f"Failed to send notification for {event_type}: {e}")
