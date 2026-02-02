from typing import Optional
import logging
import httpx


from src.application.dtos.payment import PaymentCreateDTO, PaymentReadDTO
from src.application.exceptions import PaymentCreationError
from src.application.interfaces.http_clients import PaymentsServiceAPIProtocol

logger = logging.getLogger(__name__)


class PaymentsServiceAPI(PaymentsServiceAPIProtocol):
    def __init__(self, base_url: str, api_key: str, callback_url: str):
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._callback_url = callback_url

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
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(
                    url,
                    headers={"X-API-Key": self._api_key},
                    json=payload,
                    timeout=10.0,
                )
                response.raise_for_status()

                return PaymentReadDTO(**response.json())

            except httpx.HTTPStatusError as exc:
                logger.error(
                    "Payment API Error: status=%s, response=%s",
                    exc.response.status_code,
                    exc.response.text,
                )
                raise PaymentCreationError(
                    f"Payment API returned {exc.response.status_code}: {exc.response.text}"
                )
            except (httpx.RequestError, Exception) as exc:
                logger.exception(
                    "Payment connection failed or unexpected error occurred"
                )
                raise PaymentCreationError(f"Payment connection failed: {str(exc)}")
