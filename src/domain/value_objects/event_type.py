from enum import Enum


class EventTypeEnum(str, Enum):
    ORDER_NEW = "order.new"
    ORDER_SHIPPED = "order.shipped"
    ORDER_PAID = "order.paid"
    ORDER_CANCELLED = "order.cancelled"
