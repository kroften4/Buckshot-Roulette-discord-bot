import discord
from discord.ext import commands
import asyncio
import random


class Why(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(
        name='why',
        description="Ask the bot why or sth"
    )
    async def why(self, ctx):
        await ctx.response.defer()
        await asyncio.sleep(random.randint(10, 60))
        await ctx.respond('idk')


def setup(bot):
    bot.add_cog(Why(bot))
