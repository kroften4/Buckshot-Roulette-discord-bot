# import discord
# from discord.ext import commands
# from discord import option
#
#
# class Info(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot
#
#
#
#
# def setup(bot):
#     bot.add_cog(Info(bot))


# @bot.slash_command(name='help')
# async def give_help(ctx):
#     await ctx.respond(content=, embed=True, )


# @add.error
# async def add_error(ctx, error):
#     # error = getattr(exception, "original", exception)
#     if isinstance(error, commands.MissingRequiredArgument):
#         await ctx.respond('Error: *Missing required argument(s)*\n**Usage:** `k!add <ticket_owner> <new_nickname>`')
#     else:
#         await ctx.respond('*An unexpected error occurred*')
