import logging
from typing import Literal

from pydantic import BaseSettings, SecretStr

logger = logging.getLogger(__name__)


class BotSettings(BaseSettings):
    """Defines the environment variables required to run the bot."""

    GG_TOKEN: SecretStr
    GG_PLAYER_ID: int
    PLAYER_NAME: str
    DISCORD_TOKEN: SecretStr
    DISCORD_CHANNEL_ID: int
    DEPLOYED_ENVIRONMENT: Literal["dev", "test", "prod"]
    BOT_POLLING_PERIOD: int = 30
    DEFAULT_GAME_ID: int = 1386
    # DEFAULT GAME IS SMASH ULTIMATE
    LOG_FILEPATH: str | None = None
    LOG_LEVEL: int | Literal[
        "CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"
    ] = logging.DEBUG

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


bot_settings = BotSettings()  # pyright: ignore
