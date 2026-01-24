from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class PaymentDTO(BaseModel):
    order_id: UUID
    amount: Decimal
    idempotency_key: UUID


class PaymentCreateDTO(PaymentDTO):
    pass


class PaymentReadDTO(PaymentDTO):
    id: UUID
    user_id: UUID
    status: str
    idempotency_key: UUID
    created_at: datetime


class PaymentCallbackDTO(BaseModel):
    payment_id: UUID
    order_id: UUID
    status: str
    amount: Decimal
    error_message: Optional[str] = None
