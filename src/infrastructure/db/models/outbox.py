from datetime import datetime
from uuid import UUID as PyUUID
from uuid import uuid4

from sqlalchemy import JSON, UUID, DateTime, Enum, func
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.value_objects.event_type import EventTypeEnum
from src.domain.value_objects.outbox_event_status import OutboxEventStatusEnum
from .base import Base


class OutboxEventORM(Base):
    __tablename__ = "outbox_events"
    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    event_type: Mapped[EventTypeEnum] = mapped_column(
        Enum(EventTypeEnum, native_enum=False), nullable=False
    )
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[OutboxEventStatusEnum] = mapped_column(
        Enum(OutboxEventStatusEnum, native_enum=False),
        default=OutboxEventStatusEnum.PENDING,
        server_default=OutboxEventStatusEnum.PENDING.value,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"{self.id} {self.event_type} {self.status}"
