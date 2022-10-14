from discord.ext import commands, tasks

from luke_bot.smashgg_query import check_luke, get_last_bracket_run, get_last_set

bot = commands.Bot(command_prefix='!')


@bot.command('about')
async def about(ctx):
    text = 'I report updates on Luke'
    await ctx.send(text)

@bot.command('lastResult')
async def lastResult(ctx):
    text = get_last_bracket_run()
    embed = discord.Embed()
    embed.description = text
    await ctx.send(embed=embed)

def same_update(update1: str, update2: str) -> bool:
    lines1 = update1.splitlines()
    lines2 = update2.splitlines()
    if len(lines1) != len(lines2):
        return False
    for line1, line2 in zip(lines1, lines2):
        if not line1.startswith('Begins in'):
            if line1 != line2:
                return False
    return True


class LukeUpdates(commands.Cog):
    def __init__(self, bot_):
        self.bot = bot_
        self.channel_id: int = 989598751821811712
        self.most_recent_update: str = ''
        self.last_set_update: str = ''
        self.luke_updates_channel = None
        self.luke_ongoing_event_status: bool = False
        self.luke_out_of_bracket: bool = True
        self.luke_ongoing_id: int = -1
        self.luke_ongoing_event_id: int = -1
        self.send_to_luke_updates.start()

    def cog_unload(self):
        self.send_to_luke_updates.cancel()

    @tasks.loop(seconds=30)
    async def send_to_luke_updates(self):
        text, luke_active, entrant_id, event_id = check_luke()
        if text:
            if self.luke_updates_channel is None:
                self.luke_updates_channel = await self.bot.fetch_channel(self.channel_id)
            if self.luke_updates_channel is not None and not same_update(text, self.most_recent_update):
                self.most_recent_update = text
                self.luke_ongoing_event_status = luke_active
                self.luke_ongoing_id = entrant_id
                self.luke_ongoing_event_id = event_id
                embed = discord.Embed()
                embed.description = self.most_recent_update
                await self.luke_updates_channel.send(embed=embed)
            elif luke_active:
                if not self.luke_ongoing_event_status:
                    self.luke_ongoing_event_status = True
                    self.luke_out_of_bracket = False
                    self.luke_ongoing_id = entrant_id
                    self.luke_ongoing_event_id = event_id

                set_update = get_last_set(self.luke_ongoing_id, self.luke_ongoing_event_id)

                if not set_update == self.last_set_update:
                    self.last_set_update = set_update
                    embed = discord.Embed()
                    embed.description = self.last_set_update
                    await self.luke_updates_channel.send(embed=embed)
            else:
                    self.luke_ongoing_event_status = False
                    self.luke_out_of_bracket = True
                    self.luke_ongoing_id = -1
                    self.luke_ongoing_event_id = -1
                    self.last_set_update = ''


bot.add_cog(LukeUpdates(bot))
