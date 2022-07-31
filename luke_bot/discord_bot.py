import os

import discord
from discord.ext import commands, tasks

from .smashgg_query import check_luke


class BotInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command('about')
    async def about(self, ctx):
        text = 'I report updates on Luke'
        await ctx.send(text)


def same_update(update1: str, update2: str) -> bool:
    """Checks if 2 blocks of update text contain the same information"""
    lines1 = update1.splitlines()
    lines2 = update2.splitlines()
    if len(lines1) != len(lines2):
        # Different number of lines means definitely different
        return False
    for line1, line2 in zip(lines1, lines2):
        # Loop through corresponding lines, skipping the ones with relative time in them
        if line1.startswith(('Begins in', 'Started')):
            continue
        if line1 != line2:
            return False
    # Only True if all lines are the same
    return True


class LukeUpdates(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_id: int = int(os.getenv('DISCORD_CHANNEL_ID'))
        self.most_recent_update: str = ''
        self.luke_updates_channel = None
        self.send_to_luke_updates.start()

    def cog_unload(self):
        self.send_to_luke_updates.cancel()

    @tasks.loop(seconds=int(os.getenv('BOT_POLLING_PERIOD', 30)))
    async def send_to_luke_updates(self):
        text = check_luke()
        if text:
            if self.luke_updates_channel is None:
                self.luke_updates_channel = await self.bot.fetch_channel(self.channel_id)
            if self.luke_updates_channel is not None and not same_update(text, self.most_recent_update):
                self.most_recent_update = text
                embed = discord.Embed()
                embed.description = self.most_recent_update
                await self.luke_updates_channel.send(embed=embed)


def get_luke_bot(command_prefix: str = '!') -> commands.Bot:
    bot = commands.Bot(command_prefix=command_prefix)
    bot.add_cog(LukeUpdates(bot))
    bot.add_cog(BotInfo(bot))
    return bot
