import asyncio
import logging

from .discord_bot import get_luke_bot
from .settings import settings

logger = logging.getLogger()


async def main():
    discord_token: str = settings.DISCORD_TOKEN
    bot = await get_luke_bot()
    async with bot:
        await bot.start(discord_token)


if __name__ == "__main__":
    asyncio.run(main())
