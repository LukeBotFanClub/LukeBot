import logging
import asyncio

from .settings import settings
from .discord_bot import get_luke_bot

logger = logging.getLogger()


async def main():
    discord_token: str = settings.DISCORD_TOKEN
    bot = await get_luke_bot()
    async with bot:
        await bot.start(discord_token)


if __name__ == '__main__':
    asyncio.run(main())
