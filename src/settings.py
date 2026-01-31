import os
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API_KEY: Optional[str] = "px64kgKjUAwnRlHuGuE5mk0zF7gOkYHa6L12qTdjzTg"
    APP_PORT: int = 8000
    BASE_URL: Optional[str] = "https://capashi.dev-1.python-labs.ru"
    CALLBACK_URL: str = "https://leshik1305-order-service.dev-1.python-labs.ru/api"
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka.kafka.svc.cluster.local:9092"
    OUTBOX_BATCH_SIZE: int = 100
    POSTGRES_CONNECTION_STRING: str
    KAFKA_PRODUCER_TOPIC: str = "student_system_order.events"
    KAFKA_CONSUMER_TOPIC: str = "student_system_shipment.events"
    KAFKA_CONSUMER_GROUP_ID: str = ""

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "..", ".env"),
        env_file_encoding="utf-8",
    )
