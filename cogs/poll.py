# дефолт - 2 опции like/dislike
# опциональный параметр для окончания опроса спустя n времени
# опциональный параметр для добавления кнопки для завершения опроса (доступна создателю опроса и админам)

import discord
from discord.ui import Button, View
from discord.ext import commands
from discord import option


class PollButton(Button):
    def __init__(self, emoji, label, style):
        super().__init__(emoji=emoji, label=label, style=style)

    async def callback(self, interaction):
        view: View = self.view
        self.label = f"{int(self.label) + 1}"
        await interaction.response.edit_message(view=view)  # edit the message's view


class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    POLL_EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟", "<:11:1138114481843621898>",
                   "<:12:1138114480006516846>", "<:13:1138114476751728640>", "<:14:1138114473144631376>",
                   "<:15:1138114471198461952>", "<:16:1138114468224700526>", "<:17:1138114465934606387>",
                   "<:18:1138114463170568273>", "<:19:1138114460364574790>", "<:20:1138114458024157254>"]

    @discord.slash_command(
        name='poll',
        description="Create a poll"
    )
    @option('question', description="The question to ask")
    @option('options', description="How many options should the poll have (max 20)",
            min_value=0, max_value=20, default=2)
    async def poll(self, ctx, question: str, options: int):

        if options == 0:
            interaction: discord.Interaction = await ctx.respond(question)
            original_response = await interaction.original_response()
            await original_response.add_reaction("<:1984:1138138675025293353>")
        elif options == 2:
            interaction: discord.Interaction = await ctx.respond(question)
            original_response = await interaction.original_response()
            await original_response.add_reaction("✅")
            await original_response.add_reaction("<:red_crossmark:1138130077629042731>")
        else:
            interaction: discord.Interaction = await ctx.respond(question)
            original_response = await interaction.original_response()
            for i in range(options):
                await original_response.add_reaction(self.POLL_EMOJIS[i])


def setup(bot):
    bot.add_cog(Poll(bot))
