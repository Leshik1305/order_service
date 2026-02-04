import logging
from typing import Optional

import httpx
import urllib.parse
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

from src.application.dtos.payment import PaymentCreateDTO, PaymentReadDTO
from src.application.interfaces.http_clients import PaymentsServiceAPIProtocol

logger = logging.getLogger(__name__)


class PaymentsServiceAPI(PaymentsServiceAPIProtocol):
    def __init__(self, base_url: str, api_key: str, callback_url: str):
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._callback_url = callback_url
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
    async def create_payment(
        self, payment: PaymentCreateDTO
    ) -> Optional[PaymentReadDTO]:
        """Создание платежа"""
        url = urllib.parse.urljoin(self._base_url, "/api/payments")
        cb_url = self._callback_url
        payload = {
            "order_id": str(payment.order_id),
            "amount": f"{payment.amount:.2f}",
            "callback_url": cb_url,
            "idempotency_key": str(payment.idempotency_key),
        }
        logger.info(f"Отправка запроса на оплату заказа {payment.order_id}")
        logger.debug(f"URL: {url} | Payload: {payload}")

        response = await self._client.post(
            url,
            headers={"X-API-Key": self._api_key},
            json=payload,
            timeout=10.0,
        )
        logger.info(f"Получен ответ от Payment API. Статус: {response.status_code}")
        logger.debug(
            f"Заголовки ответа: {response.headers} | Тело: {response.text}",
        )
        if response.status_code >= 500:
            logger.warning(
                f"Сервер Payments вернул {response.status_code}. Тело: {response.text}. Ожидаю ретрая..."
            )
            response.raise_for_status()
        response.raise_for_status()
        logger.info(f"Платеж успешно создан")
        return PaymentReadDTO(**response.json())
