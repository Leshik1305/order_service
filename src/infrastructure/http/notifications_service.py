import logging
from typing import Any, Dict
import urllib.parse
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
        url = urllib.parse.urljoin(self._base_url, "/api/notifications")
        payload = {
            "message": message,
            "order_id": str(order_id),
            "idempotency_key": idempotency_key,
        }

        logger.info(
            "Отправка уведомления: order_id=%s, idempotency_key=%s",
            order_id,
            idempotency_key,
        )
        response = await self._client.post(
            url,
            headers={"X-API-Key": self._api_key},
            json=payload,
            timeout=10.0,
        )
        logger.info(f"Получен ответ: статус={response.status_code}, url={url}")

        logger.debug(
            f"Заголовки ответа: {response.headers} | Тело: {response.text}",
        )

        if response.status_code >= 500:
            logger.error(
                f"Ошибка сервера {response.status_code} для order_id={order_id}. Инициирую повтор..."
            )
            response.raise_for_status()
        response.raise_for_status()
        logger.info(f"Уведомление успешно отправлено для order_id={order_id}")

        return response.json()
