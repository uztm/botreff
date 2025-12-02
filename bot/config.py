# bot/config.py
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

    BOT_TOKEN: str
    CHANNEL_1: str
    CHANNEL_2: str
    BOT_USERNAME: str
    ADMIN_IDS: List[int]
    ADMIN_PANEL_TOKEN: str
    DATABASE_PATH: str
    PRIVATE_GROUP_LINK: str

settings = Settings()
