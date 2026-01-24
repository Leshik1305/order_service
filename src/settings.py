import os
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_PORT: int = 8000
    CALLBACK_URL: str
    POSTGRES_CONNECTION_STRING: str
    BASE_URL: Optional[str] = "http://localhost"
    API_KEY: Optional[str] = "default_key"
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "..", ".env"),
        env_file_encoding="utf-8",
    )
