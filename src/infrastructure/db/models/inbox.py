from datetime import datetime

from sqlalchemy import UUID, Enum, JSON, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID as PyUUID, uuid4

from src.domain.value_objects.event_type import EventTypeEnum
from src.domain.value_objects.inbox_event_status import InboxEventStatusEnum
from src.infrastructure.db import Base


class InboxEventORM(Base):
    __tablename__ = "inbox_messages"

    idempotency_key: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, unique=True, nullable=False
    )
    event_type: Mapped[EventTypeEnum] = mapped_column(
        Enum(EventTypeEnum, native_enum=False)
    )
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[InboxEventStatusEnum] = mapped_column(
        Enum(InboxEventStatusEnum, native_enum=False),
        default=InboxEventStatusEnum.PENDING,
        server_default=InboxEventStatusEnum.PENDING.value,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    processed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    def __repr__(self):
        return f"InboxEvent {self.idempotency_key} {self.event_type} {self.status}"
