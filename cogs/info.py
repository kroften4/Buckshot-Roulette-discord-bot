import discord
from discord.ext import commands
from discord import option
import datetime
import time
import pyperclip  # pyperclip.copy('stuff to add to the clipboard')


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class CopyIDButton(discord.ui.View):
        member_id_str = ""

        @discord.ui.button(label="Copy ID", style=discord.ButtonStyle.primary, emoji="📋")
        async def button_callback(self, button, interaction):
            pyperclip.copy(self.member_id_str)
            await interaction.response.send_message("ID copied to clipboard", ephemeral=True)

    @discord.slash_command(name='info', description="Get info about a user")
    @option("member", description="Member that you want to get info about")
    async def get_info_slash_command(self, ctx, member: discord.Member):
        # пока что выдаёт время UTC вместо локального, тк иначе выдаёт ошибку
        # TypeError: can't subtract offset-naive and offset-aware datetimes
        joined_duration = datetime.datetime.now(datetime.timezone.utc) - member.joined_at
        joined_at = f"<t:{int(time.mktime(member.joined_at.timetuple()))}:R>"
        days_since_joined = round(int(joined_duration.total_seconds()) / (60 * 60 * 24))
        created_duration = datetime.datetime.now(datetime.timezone.utc) - member.created_at
        created_at = f"<t:{int(time.mktime(member.created_at.timetuple()))}:R>"
        days_since_created = round(int(created_duration.total_seconds()) / (60 * 60 * 24))
        copy_id_object = self.CopyIDButton()
        copy_id_object.member_id_str = str(member.id)
        await ctx.respond(
            f'**Info for** {member}**:**\n'
            f'**Account creation date:** {created_at} / {days_since_created} days\n'
            f'**Join date:** {joined_at} / {days_since_joined} days\n'
            f'**ID:** {member.id}',
            view=copy_id_object
        )

    @discord.user_command(name='User info')
    async def get_info_user_command(self, ctx, member: discord.Member):
        # пока что выдаёт время UTC вместо локального, тк иначе выдаёт ошибку
        # TypeError: can't subtract offset-naive and offset-aware datetimes
        joined_duration = datetime.datetime.now(datetime.timezone.utc) - member.joined_at
        joined_at = f"<t:{int(time.mktime(member.joined_at.timetuple()))}:R>"
        days_since_joined = round(int(joined_duration.total_seconds()) / (60 * 60 * 24))
        created_duration = datetime.datetime.now(datetime.timezone.utc) - member.created_at
        created_at = f"<t:{int(time.mktime(member.created_at.timetuple()))}:R>"
        days_since_created = round(int(created_duration.total_seconds()) / (60 * 60 * 24))
        copy_id_object = self.CopyIDButton()
        copy_id_object.member_id_str = str(member.id)
        await ctx.respond(
            f'**Info for** {member}**:**\n'
            f'**Account creation date:** {created_at} / {days_since_created} days\n'
            f'**Join date:** {joined_at} / {days_since_joined} days\n'
            f'**ID:** {member.id}',
            ephemeral=True,
            view=copy_id_object
        )


def setup(bot):
    bot.add_cog(Info(bot))
