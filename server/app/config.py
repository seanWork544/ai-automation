from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./lifstack.db"
    upload_dir: Path = Path("uploads")
    jwt_secret: str = "change-me"
    access_token_expire_minutes: int = 60 * 24

    class Config:
        env_prefix = "LIFESTACK_"
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    return settings
