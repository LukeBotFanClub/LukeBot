from discord.ext import commands


def get_tester_bot():
    """Second bot used to assess the functionality of the main bot in testing. Functionality not yet implemented"""
    bot = commands.Bot(command_prefix='?')
    return bot
