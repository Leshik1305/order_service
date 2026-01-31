from enum import Enum


class EventTypeEnum(str, Enum):
    ORDER_CREATED = "order.created"
    ORDER_SHIPPED = "order.shipped"
    ORDER_PAID = "order.paid"
    ORDER_CANCELLED = "order.cancelled"
