import discord
from discord.ext import commands
import time


class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(
        name='ping',
        description="Get bot's latency"
    )
    async def ping(self, ctx):
        # await ctx.respond(f"Pong! {round(self.bot.latency * 1000)}ms")
        before = time.monotonic()
        await ctx.response.defer()
        # message = await ctx.respond(content="Pinging...")
        await ctx.respond(content=f"🏓 Pong! ({round((time.monotonic() - before) * 1000)}ms)")


def setup(bot):
    bot.add_cog(Ping(bot))
