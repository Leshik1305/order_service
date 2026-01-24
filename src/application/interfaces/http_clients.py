from typing import Protocol
from uuid import UUID


class CatalogServiceAPIProtocol(Protocol):

    async def check_available_qty(self, item_id: UUID, quantity) -> bool:
        pass


class PaymentsServiceAPIProtocol(Protocol):

    async def create_payment(self, payment):
        pass
