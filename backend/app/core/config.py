from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Xiaoxianji API"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://xiaoxianji:xiaoxianji@db:5432/xiaoxianji"
    jwt_secret: str = "CHANGE_ME_IN_ENV"
    formal_service_connected: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
