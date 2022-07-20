import os
import time

from luke_bot.discord_bot import bot, send_to_luke_updates
from luke_bot.smashgg_query import check_luke


def main():
    discord_token = os.getenv('DISCORD_TOKEN')

    try:
        bot.loop.run_until_complete(bot.start(discord_token))
        query = check_luke()
        if query:
            # send_to_luke_updates(query)
            print(query)
            time.sleep(60)
    except KeyboardInterrupt:
        bot.loop.run_until_complete(bot.close())

    finally:
        bot.loop.close()
