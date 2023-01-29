import os
import logging
import dataclasses
from typing import Literal

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger()


@dataclasses.dataclass
class Settings:
    """Defines the environment variables required to run the bot"""
    GG_TOKEN: str
    GG_PLAYER_ID: int
    PLAYER_NAME: str
    DISCORD_TOKEN: str
    DISCORD_CHANNEL_ID: int
    DEPLOYED_ENVIRONMENT: Literal["dev", "test", "prod"]
    BOT_POLLING_PERIOD: int = 30

    @classmethod
    def from_environment(cls):
        logger.info('Checking environment variables...')
        settings_ = cls(**{f.name: os.getenv(f.name) for f in dataclasses.fields(cls)})
        logger.info('Environment variables validated')
        return settings_


settings = Settings.from_environment()
