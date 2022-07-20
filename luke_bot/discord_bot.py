from typing import Optional

from discord import TextChannel
from discord.ext import commands, tasks

from luke_bot.smashgg_query import check_luke

bot = commands.Bot(command_prefix='!')


@bot.command('about')
async def about(ctx):
    text = 'I report updates on Luke'
    await ctx.send(text)


class LukeUpdates(commands.Cog):
    def __init__(self, bot_):
        self.bot = bot_
        self.channel_id: int = 989598751821811712
        self.most_recent_update: str = ''
        self.luke_updates_channel = None
        self.send_to_luke_updates.start()

    def cog_unload(self):
        self.send_to_luke_updates.cancel()

    @tasks.loop(seconds=30)
    async def send_to_luke_updates(self):
        print('looping')
        text = check_luke()
        if text:
            print('got text')
            if self.luke_updates_channel is None:
                self.luke_updates_channel = await self.bot.fetch_channel(self.channel_id)
            if self.luke_updates_channel is not None and text != self.most_recent_update:
                self.most_recent_update = text
                await self.luke_updates_channel.send(text)


bot.add_cog(LukeUpdates(bot))
