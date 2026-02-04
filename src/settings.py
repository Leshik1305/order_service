import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API_KEY: str
    APP_PORT: int
    BASE_URL: str
    CALLBACK_URL: str
    KAFKA_BOOTSTRAP_SERVERS: str
    OUTBOX_BATCH_SIZE: int = 100
    POSTGRES_CONNECTION_STRING: str
    KAFKA_PRODUCER_TOPIC: str
    KAFKA_CONSUMER_TOPIC: str
    KAFKA_CONSUMER_GROUP_ID: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "..", ".env"),
        env_file_encoding="utf-8",
    )
