import os

from luke_bot.discord_bot import bot


def main():
    environment_variables = ('GG_TOKEN', 'DISCORD_TOKEN', 'DISCORD_CHANNEL_ID')

    for var in environment_variables:
        if os.getenv(var) is None:
            raise RuntimeError(f'Environment variable {var} not set.')

    discord_token = os.getenv('DISCORD_TOKEN')
    bot.run(discord_token)
