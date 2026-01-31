from enum import Enum


class InboxEventStatusEnum(str, Enum):
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"
