import os
from dotenv import load_dotenv
load_dotenv()

from .discord_bot import get_luke_bot  # noqa


def main():
    environment_variables = ('GG_TOKEN', 'DISCORD_TOKEN', 'DISCORD_CHANNEL_ID')

    for var in environment_variables:
        if os.getenv(var) is None:
            raise RuntimeError(f'Environment variable {var} not set.')

    discord_token = os.getenv('DISCORD_TOKEN')
    bot = get_luke_bot()
    bot.run(discord_token)
