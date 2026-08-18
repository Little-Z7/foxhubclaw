from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FOXHUB_", extra="ignore")

    mode: str = "web"  # web | desktop
    secret_key: str = "change-this-foxhubclaw-secret-key!!"
    database_url: str = "sqlite:///./data/foxhubclaw.sqlite3"
    data_dir: Path = Path("./data")
    host: str = "127.0.0.1"
    port: int = 8787
    token_hours: int = 72
    cors_origins: str = "*"

    @property
    def auth_required(self) -> bool:
        return self.mode != "desktop"

    @property
    def reports_dir(self) -> Path:
        return self.data_dir / "reports"


settings = Settings()
