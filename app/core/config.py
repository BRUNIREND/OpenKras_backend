# app/core/config.py — должен выглядеть примерно так
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    database_url: str
    project_name: str = "Аудио-гид Красноярского музея"
    api_v1_str: str = "/api/v1"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

# Вот эта строка ОБЯЗАТЕЛЬНА — именно она экспортирует settings
settings = Settings()