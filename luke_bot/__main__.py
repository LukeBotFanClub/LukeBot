import asyncio
import logging

from .discord_bot import get_luke_bot
from .log import initialise_logger
from .settings import bot_settings

logger = logging.getLogger(__name__)


async def main():
    initialise_logger()
    discord_token: str = bot_settings.DISCORD_TOKEN.get_secret_value()
    bot = await get_luke_bot()
    async with bot:
        await bot.start(discord_token)


if __name__ == "__main__":
    asyncio.run(main())
