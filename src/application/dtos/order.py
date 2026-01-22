from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from src.domain.value_objects.order_status import OrderStatusEnum


class OrderDTO(BaseModel):
    id: UUID
    item_id: UUID
    quantity: int
    idempotency_key: UUID
    status: OrderStatusEnum
    created_at: datetime
    update_at: datetime


class OrderCreateDTO(BaseModel):
    item_id: UUID
    quantity: int
    idempotency_key: UUID = Field(default_factory=uuid4)


class OrderReadDTO(BaseModel):
    id: UUID
    item_id: UUID
    quantity: int
    status: OrderStatusEnum
    created_at: datetime
    update_at: datetime

    model_config = ConfigDict(from_attributes=True)
