import os

from luke_bot.discord_bot import bot


def main():
    discord_token = os.getenv('DISCORD_TOKEN')
    bot.run(discord_token)
