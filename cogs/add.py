import discord
from discord.ext import commands
from discord import option


class Add(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(
        name='add',
        description='Add a user to the server (For admins only)'
    )
    @commands.has_permissions(administrator=True)  # нужно посмотреть документацию pycord на этот счет
    @commands.guild_only()
    @option("ticket owner", description="Member that you want to add")
    @option("minecraft nickname", description="Minecraft nickname that you want to add to the whitelist "
                                              "and change member's server nickname to")
    async def add(self, ctx, ticket_owner: discord.Member, minecraft_nickname):
        try:
            await ticket_owner.edit(nick=minecraft_nickname)
        except Exception:
            await ctx.respond("I am forbidden to edit this member's nickname")
            return
        try:
            direct_message = await ticket_owner.create_dm()
            await direct_message.send(f'**{ticket_owner.name}**, Вы были приняты на сервер Tridemy!\n'
                                      f'Ваш minecraft-ник: **{minecraft_nickname}**')
        except Exception:
            await ctx.respond("I am not allowed to DM this member")
            return
        await ctx.respond('User was successfully added')

    # @add.error
    # async def on_application_command_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
    #     if str(error.original) == '403 Forbidden (error code: 50013): Missing Permissions':
    #         await ctx.respond("I am missing permissions required to run this command (Forbidden)\n"
    #                           "The member might have", ephemeral=True)


def setup(bot):
    bot.add_cog(Add(bot))
