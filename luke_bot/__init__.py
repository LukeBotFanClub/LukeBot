import os

from dotenv import load_dotenv

from luke_bot.discord_bot import bot

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

if __name__ == '__main__':
    bot.run(DISCORD_TOKEN)
