from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ISSUEFLOW_")

    database_url: str = f"sqlite:///{BACKEND_ROOT / 'issueflow.db'}"
    debug: bool = True


settings = Settings()
