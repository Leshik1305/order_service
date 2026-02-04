import logging
import urllib.parse
from typing import Optional
from uuid import UUID

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

from src.application.dtos.item import ItemDTO
from src.application.exceptions import (
    IsAvailableQtyError,
    ItemNotFoundError,
)
from src.application.interfaces.http_clients import (
    CatalogServiceAPIProtocol,
)

logger = logging.getLogger(__name__)


class CatalogServiceAPI(CatalogServiceAPIProtocol):
    def __init__(self, base_url: str, api_key: str):
        self._base_url = base_url
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
    async def check_available_qty(
        self, item_id: UUID, quantity: int
    ) -> Optional[ItemDTO]:
        """Проверка достаточного количества товара"""
        url = urllib.parse.urljoin(self._base_url, f"/api/catalog/items/{item_id}")
        logger.info(
            f"Запрос в каталог: проверка товара {item_id}, нужно {quantity} шт."
        )
        response = await self._client.get(
            url,
            headers={"X-API-Key": self._api_key},
            timeout=10.0,
        )
        logger.info(f"Каталог ответил: статус={response.status_code}")
        if response.status_code == 404:
            logger.error(f"Товар {item_id} не найден в каталоге (404)")
            raise ItemNotFoundError(f"Item {item_id} not found in catalog")

        if response.is_error:
            logger.warning(
                f"Ошибка Catalog API: {response.status_code} | Тело: {response.text}"
            )

        response.raise_for_status()

        data = response.json()
        available_qty = data.get("available_qty", 0)

        if available_qty < quantity:
            logger.warning(
                f"Недостаточно товара {item_id}: заказано {quantity}, в наличии {available_qty}"
            )
            raise IsAvailableQtyError(
                f"Not enough stock. Requested: {quantity}, available: {available_qty}"
            )
        logger.info(f"Товар {item_id} доступен ({available_qty} шт.)")
        item = ItemDTO(**data)
        return item
