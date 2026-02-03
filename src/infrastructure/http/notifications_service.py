import logging
from typing import Dict, Any

import httpx

logger = logging.getLogger(__name__)


class NotificationsServiceAPI:
    def __init__(self, base_url: str, api_key: str):
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._client = httpx.AsyncClient()

    async def send_notification(
        self, message: str, idempotency_key: str, order_id: str
    ) -> Dict[str, Any]:
        url = f"{self._base_url}/api/notifications"
        payload = {
            "message": message,
            "order_id": str(order_id),
            "idempotency_key": idempotency_key,
        }

        try:
            print("Отправляю запрос")
            response = await self._client.post(
                url,
                headers={"X-API-Key": self._api_key},
                json=payload,
                timeout=10.0,
            )
            print("получил ответ")
            response.raise_for_status()
            print("получил правильный ответ")

            return response.json()

        except httpx.HTTPStatusError as exc:
            logger.error(
                f"Notification service error: {exc.response.status_code} - {exc.response.text}"
            )

        except (httpx.RequestError, Exception) as exc:
            logger.exception(
                f"Network error while reaching notification service: {exc}"
            )
