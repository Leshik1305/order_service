from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from src.domain.value_objects.order_status import OrderStatusEnum


class OrderDTO(BaseModel):
    id: UUID
    item_id: UUID
    user_id: str
    quantity: int
    amount: Decimal
    idempotency_key: UUID
    status: OrderStatusEnum
    created_at: datetime
    update_at: datetime


class OrderCreateDTO(BaseModel):
    user_id: str
    item_id: UUID
    quantity: int
    idempotency_key: UUID = Field(default_factory=uuid4)


class OrderReadDTO(BaseModel):
    id: UUID
    user_id: str
    item_id: UUID
    quantity: int
    status: OrderStatusEnum
    # amount: Decimal
    created_at: datetime
    update_at: datetime

    model_config = ConfigDict(from_attributes=True)
