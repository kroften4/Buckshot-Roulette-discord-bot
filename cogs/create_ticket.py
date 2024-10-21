#   1. Сделать дб с номерами и ID тикетов и их авторами, чтобы считать тикеты в имени канала и чтобы один юзер
#       не мог создавать больше 1 тикета.
#   2. В созданном по кнопке канале настраиваются нужные пермишны, отправляется сообщение с полями ввода текста
#       (UI components). 1 поле ввода под никнейм (он сохраняется в дб, наверное). Второе поле ввода (хотя удобнее
#       возможно просто чтобы юзер отправлял отдельное сообщение снизу, посмотрим) - для остальной информации
#   3. Команда /ticket accept (вместо /add) Поскольку используется поле ввода, аргумент с никнеймом можно убрать.
#       Если лс юзера закрыт, отправляется close request на 24 часа в канал тикета. Команда должна менять роли мемберу
#   4. Команда /ticket deny по аналогии
#   5. rcon??? - добавление никнейма из дб в вайтлист
#   6. Идея: сделать канал alerts для админов чтобы туда бот писал какие-то предупреждения или еще что-то
#   7. Возможно будет проще взаимодействовать с существующим тикет ботом (но это для лузеров)
#   8. штука с txt файлом не работает (во-первых он общий для всей guilds, во вторых если неск. человек одновременно
#       нажмут кнопку, то он не успеет обновиться и создадутся 2 канала с одинаковым номером) что делать то???
#   9. Посмотреть опен сорс тикет ботов
#   10. Настроить пермишны для команд (например, ticket send-ticket-create-message должен использоваться только
#       модерами). Посмотреть разные способы настройки пермишнов (можно ли скрыть команду для всех кроме админов?)
#   11. Почему ошибки выводятся в консоль, а не в файл???
#   12. Команда poll с аргументом для кол-ва опций (2 по дефолту)
#   13. субклассинг бота
#   14. повозиться с гитхабом (бекапы + интеграция проекта на пк или типа того)
#   16. кнопка открытия тикета не постоянная, сбрасывается при перезапуске

import discord
from discord.commands import SlashCommandGroup, Option
from discord.ext import commands


class CreateTicket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class CreateTicketButton(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(label="Create ticket", style=discord.ButtonStyle.primary, emoji="📝")
        async def button_callback(self, button, interaction):
            with open('cogs/tickets_counter.txt', 'r') as file:
                # read a list of lines into data
                tickets_counter = file.readline()
            tickets_counter = str(int(tickets_counter) + 1)
            category = discord.utils.get(interaction.guild.categories, name='krftn sus5y bot')
            ticket_channel = await interaction.guild.create_text_channel(f"ticket-{tickets_counter[0]}",
                                                                         category=category)
            with open('cogs/tickets_counter.txt', 'w') as file:
                file.writelines(str(tickets_counter))
            await ticket_channel.send("Write your request here")
            await interaction.response.send_message(f"New ticket created in {ticket_channel.mention}", ephemeral=True)

    ticket = SlashCommandGroup("ticket", "Ticket commands")

    @ticket.command(name='send-create-message', description="Sends a special message with 'Create ticket' button")
    # @option("channel", description="Channel to send the message to")
    async def send_create_ticket_message(self, ctx: discord.ApplicationContext,
                                         channel: Option(discord.TextChannel, "The channel to send the message to",
                                                         required=False)):
        if channel is None:
            await ctx.respond(f'Sending a create ticket message in {ctx.channel.mention}', ephemeral=True)
            await ctx.send("An embed is eventually gonna end up here", view=self.CreateTicketButton())
        else:
            create_ticket_button_obj = self.CreateTicketButton()
            create_ticket_button_obj.channel = channel
            await ctx.respond(f"Sending a create ticket message in {channel.mention}", ephemeral=True)
            await channel.send("An embed is eventually going to end up here", view=create_ticket_button_obj)

        # await ctx.send("An embed is eventually gonna end up here", view=self.CreateTicketButton())

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        channel = discord.utils.get(guild.channels, name='create-ticket')
        await member.send(f"Welcome to {guild}!\nCreate a new ticket in {channel.mention}")


def setup(bot):
    bot.add_cog(CreateTicket(bot))
