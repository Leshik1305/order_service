from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.domain.value_objects.event_type import EventTypeEnum


class InboxCreateDTO(BaseModel):
    idempotency_key: UUID
    event_type: EventTypeEnum
    payload: [str, Any]


class InboxReadDTO(BaseModel):
    idempotency_key: UUID
    event_type: EventTypeEnum
    payload: Dict[str, Any]
    status: str
    created_at: datetime
    processed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
