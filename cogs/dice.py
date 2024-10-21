import discord
from discord.ext import commands
import random
from discord import option


class Dice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(
        name='dice',
        description='Roll a dice'
    )
    @option(name='faces', description='Amount of faces (6 by default)', required=False, default=6, min_value=0)
    @option(name='rolls', description='Amount of rolls (1 by default)', required=False, default=1, min_value=0)
    async def dice(self, ctx, faces: int, rolls: int):
        if faces <= 0:
            if rolls == 1:
                await ctx.respond("** **")
            else:
                await ctx.respond(", ".join(["" for n in range(1, rolls + 1)]))
        else:
            await ctx.respond(', '.join([str(random.randint(1, faces)) for n in range(1, rolls + 1)]))


def setup(bot):
    bot.add_cog(Dice(bot))
