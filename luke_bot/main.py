import os
import logging
import dataclasses
import sys
import asyncio

from dotenv import load_dotenv

load_dotenv()

from .discord_bot import get_luke_bot  # noqa: E402

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))


@dataclasses.dataclass
class EnvironmentVariables:
    """Defines the environment variables required to run the bot"""
    GG_TOKEN: str
    GG_PLAYER_ID: int
    PLAYER_NAME: str
    DISCORD_TOKEN: str
    DISCORD_CHANNEL_ID: int
    BOT_POLLING_PERIOD: int | None

    @classmethod
    def validate(cls):
        cls(**{f.name: os.getenv(f.name) for f in dataclasses.fields(cls)})


async def main():
    logger.info('Checking environment variables...')
    EnvironmentVariables.validate()
    logger.info('Environment variables validated')
    discord_token: str = os.environ['DISCORD_TOKEN']
    bot = await get_luke_bot()
    async with bot:
        await bot.start(discord_token)


if __name__ == '__main__':
    asyncio.run(main())
