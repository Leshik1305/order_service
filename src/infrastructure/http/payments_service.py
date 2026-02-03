from typing import Optional

import httpx

from src.application.dtos.payment import PaymentCreateDTO, PaymentReadDTO
from src.application.exceptions import PaymentCreationError
from src.application.interfaces.http_clients import PaymentsServiceAPIProtocol


class PaymentsServiceAPI(PaymentsServiceAPIProtocol):
    def __init__(self, base_url: str, api_key: str, callback_url: str):
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._callback_url = callback_url
        self._client = httpx.AsyncClient()

    async def create_payment(
        self, payment: PaymentCreateDTO
    ) -> Optional[PaymentReadDTO]:
        url = f"{self._base_url}/api/payments"
        cb_url = f"{self._callback_url}/orders/payment-callback"
        payload = {
            "order_id": str(payment.order_id),
            "amount": f"{payment.amount:.2f}",
            "callback_url": cb_url,
            "idempotency_key": str(payment.idempotency_key),
        }
        try:
            response = await self._client.post(
                url,
                headers={"X-API-Key": self._api_key},
                json=payload,
                timeout=20.0,
            )
            response.raise_for_status()

            return PaymentReadDTO(**response.json())

        except httpx.HTTPStatusError as exc:
            # Логируем ошибку для отладки
            print(f"Payment API Error: {exc.response.text}")
            raise PaymentCreationError(
                f"Payment API returned {exc.response.status_code}"
            )
        except Exception as exc:
            raise PaymentCreationError(f"Payment connection failed: {str(exc)}")
