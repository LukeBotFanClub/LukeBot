from typing import Optional

from discord import TextChannel
from discord.ext import commands

bot = commands.Bot(command_prefix='!')


@bot.command(name='q')
async def basic_query(ctx):
    text = 'test'
    await ctx.send(text)


def send_to_luke_updates(text: str):
    channel_id = 989598751821811712
    luke_updates: Optional[TextChannel] = bot.get_channel(channel_id)
    if luke_updates is not None:
        luke_updates.send(text)
