from discord.ext import commands

bot = commands.Bot(command_prefix='!')


@bot.command(name='q')
async def basic_query(ctx):
    text = 'test'
    await ctx.send(text)
