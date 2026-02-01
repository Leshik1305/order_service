from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.domain.value_objects.event_type import EventTypeEnum
from src.domain.value_objects.outbox_event_status import OutboxEventStatusEnum


class OutboxEventDTO(BaseModel):
    id: UUID | str
    event_type: str
    status: str
    payload: dict
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class OutboxCreateDTO(BaseModel):
    event_type: EventTypeEnum
    payload: dict
    status: OutboxEventStatusEnum = OutboxEventStatusEnum.PENDING
