from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import Enum, DateTime, func, UUID, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.value_objects.order_status import OrderStatusEnum
from src.infrastructure.db import Base


class OrderORM(Base):
    __tablename__ = "orders"
    __table_args__ = {"extend_existing": True}

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    item_id: Mapped[UUID] = mapped_column(UUID, nullable=False)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    idempotency_key: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    status: Mapped[OrderStatusEnum] = mapped_column(
        Enum(OrderStatusEnum, native_enum=False), default=OrderStatusEnum.NEW
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    update_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"Order number {id}, status={self.status}"
