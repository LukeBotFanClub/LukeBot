import logging

from discord import app_commands, Intents, Embed, Interaction
from discord.ext import tasks, commands
from discord.message import Message

from .settings import settings
from .smashgg_query import check_luke, get_last_bracket_run, get_last_set

logger = logging.getLogger(__name__)

PLAYER_NAME: str = settings.PLAYER_NAME
HELP_TEXT = f'I report updates on {PLAYER_NAME} by polling the start.gg API.'


def same_update(update1: str, update2: str) -> bool:
    """Checks if 2 blocks of update text contain the same information"""
    lines1 = update1.strip().splitlines()
    lines2 = update2.strip().splitlines()
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


class LukeCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__()

    @commands.command(name="sync")
    async def sync(self, ctx: commands.Context):
        """Syncs slash commands with discord"""
        # This copies the global commands over to your guild.
        guild = ctx.guild
        if guild is not None:
            self.bot.tree.copy_global_to(guild=guild)
            synced_cmds = await self.bot.tree.sync(guild=guild)
            logger.info(f'{synced_cmds = }')
            await ctx.send(f"Synced commands: {synced_cmds}")
        else:
            await ctx.send("Failed to indentify guild. This shouldn't ever happen really.")

    @app_commands.command(name="results", description=f"Post {PLAYER_NAME}'s latest results")
    async def results(self, interaction: Interaction):
        """Manually invoke an update, and have the bot post it to the channel where it was invoked"""
        embed = Embed()
        embed.description = str(check_luke())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="last_run", description=f"Post {PLAYER_NAME}'s last bracket run results'")
    async def last_run(self, interaction: Interaction):
        text = get_last_bracket_run()
        embed = Embed()
        embed.description = text
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="current_set", description=f"Post {PLAYER_NAME}'s most recent ongoing set result'")
    async def current_set(self, interaction: Interaction):
        text = get_last_set()
        embed = Embed()
        embed.description = text
        await interaction.response.send_message(embed=embed)


class LukeBot(commands.Bot):
    """This bot reports tournament results by polling tye start.gg API"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_id: int = int(settings.DISCORD_CHANNEL_ID)
        self.most_recent_update: str = ''
        self.luke_updates_channel = None

    async def setup_hook(self) -> None:
        self.send_to_luke_updates.start()

    async def on_ready(self):
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})')

    @tasks.loop(seconds=int(settings.BOT_POLLING_PERIOD))
    async def send_to_luke_updates(self):
        """Polls the start.gg API for latest results. If there's new info, an update is posted to the updates channel"""
        text = check_luke()
        if text:
            if self.luke_updates_channel is None:
                self.luke_updates_channel = self.get_channel(self.channel_id)
            if self.luke_updates_channel is not None and not same_update(text, self.most_recent_update):
                self.most_recent_update = text
                embed = Embed()
                embed.description = self.most_recent_update
                await self.luke_updates_channel.send(embed=embed)

    @send_to_luke_updates.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  # wait until the bot logs in
        # Set most recent update to the content of the most recent message
        if self.luke_updates_channel is None:
            self.luke_updates_channel = self.get_channel(self.channel_id)
        last_message = None
        async for message in self.luke_updates_channel.history(limit=15, oldest_first=False):
            if message.author == self.user:
                last_message = message
                break

        if last_message is not None and last_message.embeds:
            content = last_message.embeds[0].description
            if isinstance(content, str):
                self.most_recent_update = content

    async def process_commands(self, message: Message, /) -> None:
        if settings.DEPLOYED_ENVIRONMENT != "test":
            # Allows tester bot to invoke commands
            await super().process_commands(message)
        else:
            # Below is copied from the super class's implementation
            ctx = await self.get_context(message)
            # the type of the invocation context's bot attribute will be correct
            await self.invoke(ctx)  # type: ignore


async def get_luke_bot() -> LukeBot:
    intents = Intents(
        guild_messages=True, guilds=True, messages=True, message_content=True,
        members=False,
        auto_moderation=False, auto_moderation_configuration=False, auto_moderation_execution=False,
        bans=False, dm_messages=False, dm_reactions=False, dm_typing=False, emojis=False, emojis_and_stickers=False,
        guild_reactions=False, guild_scheduled_events=False, guild_typing=False, integrations=False, invites=False,
        presences=False, reactions=False, typing=False, value=False, voice_states=False, webhooks=False,
    )
    bot = LukeBot(intents=intents, command_prefix=commands.when_mentioned)
    commands_cog = LukeCommands(bot)
    await bot.add_cog(commands_cog)
    return bot
