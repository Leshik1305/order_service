import logging
import urllib.parse
from typing import Optional
from uuid import UUID

import httpx

from src.application.dtos.item import ItemDTO
from src.application.exceptions import (
    ItemNotFoundError,
    IsAvailableQtyError,
)
from src.application.interfaces.http_clients import (
    CatalogServiceAPIProtocol,
)

logger = logging.getLogger(__name__)


class CatalogServiceAPI(CatalogServiceAPIProtocol):

    def __init__(self, base_url: str, api_key: str):
        self._base_url = base_url
        self._api_key = api_key

    async def check_available_qty(
        self, item_id: UUID, quantity: int
    ) -> Optional[ItemDTO]:
        url = urllib.parse.urljoin(self._base_url, f"/api/catalog/items/{item_id}")
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                url,
                headers={"X-API-Key": self._api_key},
            )
            if response.status_code == 404:
                logger.warning("Item %s not found in catalog", item_id)
                raise ItemNotFoundError(f"Item {item_id} not found in catalog")
            response.raise_for_status()
            data = response.json()
            available_qty = data.get("available_qty", 0)

            if available_qty < quantity:
                logger.info(
                    f"Stock shortage for item {item_id}: requested {quantity}, available {available_qty}",
                )
                raise IsAvailableQtyError(
                    f"Not enough stock. Requested: {quantity}, available: {available_qty}"
                )
            item = ItemDTO(**response.json())
            return item
