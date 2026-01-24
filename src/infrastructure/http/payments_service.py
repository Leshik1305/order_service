import urllib.parse
from typing import Optional

import httpx

from src.application.dtos.payment import PaymentCreateDTO, PaymentReadDTO
from src.application.exceptions import PaymentCreationError
from src.application.interfaces.http_clients import PaymentsServiceAPIProtocol


class PaymentsServiceAPI(PaymentsServiceAPIProtocol):
    def __init__(self, base_url: str, api_key: str, callback_url: str):
        self._base_url = base_url
        self._api_key = api_key
        self._callback_url = callback_url
        self._client = httpx.AsyncClient()

    async def create_payment(
        self, payment: PaymentCreateDTO
    ) -> Optional[PaymentReadDTO]:
        url = urllib.parse.urljoin(self._base_url, "/api/payments")
        cb_url = urllib.parse.urljoin(self._callback_url, "/orders/payment-callback")
        payload = {
            "order_id": str(payment.order_id),
            "amount": str(payment.amount),
            "callback_url": cb_url,
            "idempotency_key": str(payment.idempotency_key),
        }
        try:
            response = await self._client.post(
                url,
                headers={"X-API-Key": self._api_key},
                json=payload,
                timeout=10.0,
            )
            response.raise_for_status()
            return PaymentReadDTO(**response.json())
        except httpx.HTTPStatusError as exc:
            raise Exception(
                f"Payment service error: {exc.response.status_code} - {exc.response.text}"
            )
        except httpx.RequestError as exc:
            raise Exception(f"Network error when accessing the payment API: {exc}")
        except Exception as exc:
            raise PaymentCreationError(f"Unexpected error: {exc}")
