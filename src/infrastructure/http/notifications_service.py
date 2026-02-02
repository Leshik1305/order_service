import logging
from typing import Dict, Any

import httpx

logger = logging.getLogger(__name__)


class NotificationsServiceAPI:
    def __init__(self, base_url: str, api_key: str):
        self._base_url = base_url.rstrip("/")
        self._headers = {"X-API-Key": api_key, "Content-Type": "application/json"}

    async def send_notification(
        self, message: str, idempotency_key: str
    ) -> Dict[str, Any]:
        url = f"{self._base_url}/api/notifications"
        payload = {"message": message, "idempotency_key": idempotency_key}

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self._headers,
                )

                response.raise_for_status()

                return response.json()

            except httpx.HTTPStatusError as e:
                logger.error(
                    f"Notification service error: {e.response.status_code} - {e.response.text}"
                )
                raise Exception(f"Failed to send notification: {e.response.text}")

            except (httpx.RequestError, Exception) as e:
                logger.exception(
                    f"Network error while reaching notification service: {e}"
                )
                raise Exception("Notification service is unavailable")
