from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
import logging

class Settings(BaseSettings):
    # Db credentials
    postgres_user: str
    postgres_host: str
    postgres_password: str
    postgres_db: str
    postgres_port: str

    # Redis cache credentials
    redis_host: str
    redis_port: str
    redis_password: str

    # Model path
    model_path: str

    # Configure after ENVIRONMENT exists
    model_config = SettingsConfigDict(
        env_file=None,
        env_file_encoding="utf-8"
    )

@lru_cache
def get_settings():
    
    env = os.getenv("ENVIRONMENT", "development").lower()
    env_file = f".env.{env}"

    logging.info(f"Loading environment: {env}, file: {env_file}")

    return Settings(
        _env_file=env_file
    )
