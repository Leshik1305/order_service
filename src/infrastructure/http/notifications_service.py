import logging
from typing import Any, Dict

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

logger = logging.getLogger(__name__)


class NotificationsServiceAPI:
    def __init__(self, base_url: str, api_key: str):
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._client = httpx.AsyncClient()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=(
            retry_if_exception_type(httpx.HTTPStatusError)
            | retry_if_exception_type(httpx.RequestError)
        ),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def send_notification(
        self, message: str, idempotency_key: str, order_id: str
    ) -> Dict[str, Any]:
        """Отправка notification"""
        url = f"{self._base_url}/api/notifications"
        payload = {
            "message": message,
            "order_id": str(order_id),
            "idempotency_key": idempotency_key,
        }

        print("Отправляю запрос")
        response = await self._client.post(
            url,
            headers={"X-API-Key": self._api_key},
            json=payload,
            timeout=10.0,
        )
        print(
            f"Получен ответ от {url}\n"
            f"Статус: {response.status_code}\n"
            f"Заголовки: {response.headers}\n"
            f"Тело (raw): {response.text}"
        )

        if response.status_code >= 500:
            print(f"Сервер вернул {response.status_code}, пробую еще раз...")
            response.raise_for_status()
        response.raise_for_status()
        print("получил правильный ответ")

        return response.json()
