import os

from discord.ext import commands

TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')


@bot.command(name='q')
async def basic_query(ctx):
    text = 'test'
    await ctx.send(text)


if __name__ == '__main__':
    bot.run(TOKEN)
