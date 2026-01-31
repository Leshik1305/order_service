from datetime import datetime
from uuid import UUID


def default_serializer(obj):
    if isinstance(obj, (datetime, UUID)):
        return str(obj)
    raise TypeError(f"Type {type(obj)} not serializable")
