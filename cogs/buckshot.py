import asyncio
import random

import discord
from discord import option
from discord.ext import commands


class GameLogic:
    class Player:
        def __init__(self, member: discord.Member, max_health: int):
            self.member = member
            self.health = max_health
            self.can_heal = True
            self.items = {'beer': 0,
                          'handcuffs': 0,
                          'saw': 0,
                          'cigarette': 0,
                          'magnifying glass': 0}

        async def edit_health(self, game_self, interaction, health_change: int):
            if self.can_heal:
                self.health += health_change
                if game_self.game_mode == 'cutoff' and self.health <= 2:
                    self.can_heal = False
                    content = f"💀 **{self.member.display_name}**, ARE YOU READY?"
                    await interaction.channel.send(content)
                return
            if health_change < 0:
                self.health = 0

    def __init__(self, player1: discord.member, player2: discord.member, max_health: int, game_mode: str = 'normal'):
        self.player1 = self.Player(member=player1, max_health=max_health)
        self.player2 = self.Player(member=player2, max_health=max_health)
        self.current_player = self.player1
        self.current_opponent = self.player2
        self.max_health = max_health
        self.game_mode = game_mode
        self.game_id = f"{player1.id}+{player2.id}"
        self.items_display = {
            'beer': {
                'emoji': '🍺',
            },
            'handcuffs': {
                'emoji': '⛓',
            },
            'saw': {
                'emoji': '🔪',
            },
            'cigarette': {
                'emoji': '🚬',
            },
            'magnifying glass': {
                'emoji': '🔍',
            }
        }

    used_saw = False
    current_round = 0
    used_handcuffs = False
    current_shell = 0
    shells = []

    def generate_stats_message(self):
        player1_emojis = ""
        player2_emojis = ""
        if self.current_player is self.player1:
            player1_emojis += "🔫"
            if self.used_saw:
                player1_emojis += " 🔪"
            if self.used_handcuffs:
                player2_emojis += ":chains:"
        else:
            player2_emojis += "🔫"
            if self.used_saw:
                player2_emojis += " 🔪"
            if self.used_handcuffs:
                player1_emojis += ":chains:"
        items_used_player1 = sum(self.player1.items.values())
        items_used_player2 = sum(self.player2.items.values())
        if self.game_mode == 'normal':
            health_player1 = '▮' * self.player1.health
            health_player2 = '▮' * self.player2.health
        else:
            health_player1 = ' **✝**' * min(self.player1.health, 2) + '▮' * max(0, self.player1.health - 2)
            health_player2 = ' **✝**' * min(self.player2.health, 2) + '▮' * max(0, self.player2.health - 2)
        if self.player1.health == 0:
            health_player1 = "DIED"
        if self.player2.health == 0:
            health_player2 = "DIED"
        st = (
            f"**{self.player1.member.display_name}** {player1_emojis}\n"
            f"{health_player1}\n"
            f"""{'  '.join([f'{emoji} x{list(self.player1.items.values())[idx]}'
                            for idx, emoji in enumerate('🍺⛓🔪🚬🔍')])}  ({items_used_player1}/8)\n\n"""
            f"**{self.player2.member.display_name}** {player2_emojis}\n"
            f"{health_player2}\n"
            f"""{'  '.join([f'{emoji} x{list(self.player2.items.values())[idx]}'
                            for idx, emoji in enumerate('🍺⛓🔪🚬🔍')])}  ({items_used_player2}/8)"""
        )
        return st

    def new_round(self):
        self.current_shell = 0
        if self.current_round != 0:
            self.current_player, self.current_opponent = self.current_opponent, self.current_player
        self.current_round += 1

        # generate shells
        batch_size = random.randint(2, 8)
        lives = batch_size // 2
        blanks = batch_size - lives
        self.shells = [0] * blanks + [1] * lives
        random.shuffle(self.shells)

        # generate items
        amount = random.randint(1, 4)
        for player in self.player1, self.player2:
            slots_left = 8 - sum(player.items.values())
            for i in range(min(amount, slots_left)):
                item = random.choice(list(player.items))
                player.items[item] += 1

    async def shoot_self(self, interaction):
        if self.shells[self.current_shell] == 1:
            if self.used_saw:
                await self.current_player.edit_health(self, interaction, -2)
            else:
                await self.current_player.edit_health(self, interaction, -1)
            if len(self.shells) != self.current_shell + 1 and not self.used_handcuffs:
                self.current_player, self.current_opponent = self.current_opponent, self.current_player
            self.used_handcuffs = False
        # if self.current_shell + 1 < len(self.shells):
        self.current_shell += 1
        self.used_saw = False

    async def shoot_opponent(self, interaction):
        # if bullet is blank, skips this part
        if self.shells[self.current_shell] == 1:
            if self.used_saw:
                await self.current_opponent.edit_health(self, interaction, -2)
            else:
                await self.current_opponent.edit_health(self, interaction, -1)
        if len(self.shells) != self.current_shell + 1 and not self.used_handcuffs:
            self.current_player, self.current_opponent = self.current_opponent, self.current_player
        self.current_shell += 1
        self.used_handcuffs = False
        self.used_saw = False

    def use_beer(self):
        self.current_player.items['beer'] -= 1
        self.current_shell += 1
        # if self.current_shell + 1 == len(self.shells):
        #     self.new_round()

    def use_handcuffs(self):
        self.used_handcuffs = True
        self.current_player.items['handcuffs'] -= 1

    def use_saw(self):
        self.used_saw = True
        self.current_player.items['saw'] -= 1

    async def use_cigarette(self, interaction):
        if self.current_player.health != self.max_health:
            await self.current_player.edit_health(self, interaction, 1)
        self.current_player.items['cigarette'] -= 1

    def use_magnifying_glass(self):
        shell = '▮' if self.shells[self.current_shell] == 1 else '▯'
        self.current_player.items['magnifying glass'] -= 1
        return shell

    async def reload_shotgun(self, interaction):
        self.new_round()
        content = "RELOADING THE SHOTGUN"
        shells_message = await interaction.followup.send(content=content)
        for i in range(4):
            await asyncio.sleep(0.1)
            content += '.'
            await interaction.followup.edit_message(shells_message.id, content=content)

        # show shells
        seconds = 5
        shells = ''.join('▮' if bullet else '▯' for bullet in self.shells)
        content = (f"**ROUNDS (DISAPPEARS IN {seconds} SECONDS):**\n"
                   f"{shells}")
        await interaction.followup.edit_message(shells_message.id, content=content)
        await asyncio.sleep(1)
        for seconds in range(seconds - 1, 0, -1):
            content = (f"**ROUNDS (DISAPPEARS IN {seconds} SECONDS):**\n"
                       f"{shells}")
            await interaction.followup.edit_message(shells_message.id, content=content)
            await asyncio.sleep(1)
        await interaction.followup.delete_message(shells_message.id)
        random.shuffle(self.shells)

        view = Buckshot.ChooseAction()
        view.game = self
        game_content = self.generate_stats_message()
        await interaction.followup.send(content=game_content, view=view)

    async def send_game_message(self, interaction):
        game_content = self.generate_stats_message()
        view = Buckshot.ChooseAction()
        view.game = self
        return await interaction.followup.send(content=game_content, view=view)

    async def check_for_win(self, interaction):
        if self.current_player.health <= 0 or self.current_opponent.health <= 0:
            await self.game_over(interaction)
            return True
        return False

    async def check_for_reload(self, interaction, used_shell_idx):
        if used_shell_idx + 1 == len(self.shells):
            await self.reload_shotgun(interaction)
            return
        await self.send_game_message(interaction)

    async def game_over(self, interaction):
        winner, looser = (self.player1, self.player2) \
            if self.player1.health > 0 \
            else (self.player2, self.player1)
        win_content = (
            f"**{looser.member.mention} DIED**\n"
            f"**WINNER: {winner.member.mention}**\n\n"
            f"{self.generate_stats_message()}"
        )

        # win_content = f"**{winner.member.mention} HAS KILLED {looser.member.mention}**\n\n" + \
        #               self.generate_stats_message()
        # await interaction.followup.send(content=game_content, view=None)
        await interaction.followup.send(win_content)


class Buckshot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class ChooseShotgun(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)
            # self.disable_on_timeout = True

        # async def on_timeout(self):
        #     self.disable_all_items()
        #     await self.message.edit(view=self)
        #     await self.message.channel.send("Game aborted after 5 minutes of AFK")

        game = None

        @discord.ui.button(label="You", style=discord.ButtonStyle.gray, emoji="🫵")
        async def button_callback_shoot_self(self, button, interaction):
            if interaction.user != self.game.current_player.member:
                await interaction.response.send_message("ain't your turn", ephemeral=True, delete_after=1.5)
                return
            current_player_name = str(self.game.current_player.member.display_name)
            used_shell_idx = int(self.game.current_shell)
            used_shell = '▮ live round' if self.game.shells[self.game.current_shell] == 1 else '▯ blank'
            used_saw = bool(self.game.used_saw)
            await self.game.shoot_self(interaction)
            game_content = self.game.generate_stats_message()
            await interaction.response.edit_message(content=game_content, view=None,
                                                    delete_after=1.5)  # delete previous game message
            item_message = f"🔫 **{current_player_name}** shoots themselves with a {used_shell}"
            if used_saw:
                item_message += " (double damage)"
            await interaction.followup.send(item_message, delete_after=5)
            await asyncio.sleep(1)

            game_over = await self.game.check_for_win(interaction)
            if not game_over:
                await self.game.check_for_reload(interaction, used_shell_idx)

        @discord.ui.button(label="Opponent", style=discord.ButtonStyle.gray, emoji="👉")
        async def button_callback_shoot_opponent(self, button, interaction):
            if interaction.user != self.game.current_player.member:
                await interaction.response.send_message("ain't your turn", ephemeral=True, delete_after=1.5)
                return
            current_player_name = str(self.game.current_player.member.display_name)
            current_opponent_name = str(self.game.current_opponent.member.display_name)
            used_shell_idx = int(self.game.current_shell)
            used_shell = '▮ live round' if self.game.shells[self.game.current_shell] == 1 else '▯ blank'
            used_saw = bool(self.game.used_saw)
            await self.game.shoot_opponent(interaction)

            game_content = self.game.generate_stats_message()
            await interaction.response.edit_message(content=game_content, view=None, delete_after=1.5)
            item_message = f"🔫 **{current_player_name}** shoots at **{current_opponent_name}** with a {used_shell}"
            if used_saw:
                item_message += " (double damage)"
            await interaction.followup.send(item_message, delete_after=5)
            await asyncio.sleep(1)

            game_over = await self.game.check_for_win(interaction)
            if not game_over:
                await self.game.check_for_reload(interaction, used_shell_idx)

    class ChooseAction(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)

        # async def on_timeout(self):
        #     self.disable_all_items()
        #     print(self)
        #     print(dir(self))
        #     print(dir(self.children[0]._interaction))
        #
        #     await self.message.edit(view=self)
        #     # await self.message.channel.send("Game aborted after 5 minutes of AFK")

        game = None

        @discord.ui.select(
            placeholder=f"Use an item",
            options=[
                discord.SelectOption(
                    emoji='🔫',
                    label="Shotgun",
                    description="Shooting yourself with a blank skips the opponent's turn"
                ),
                discord.SelectOption(
                    emoji='🍺',
                    label="Beer",
                    description="Rack the shotgun and remove the current shell"
                ),
                discord.SelectOption(
                    emoji='⛓',
                    label="Handcuffs",
                    description="Opponent skips the next turn"
                ),
                discord.SelectOption(
                    emoji='🔪',
                    label="Hand saw",
                    description="Shotgun deals 2 damage"
                ),
                discord.SelectOption(
                    emoji='🚬',
                    label="Cigarette",
                    description="Takes the edge off. Regain 1 charge"
                ),
                discord.SelectOption(
                    emoji='🔎',
                    label="Magnifying glass",
                    description="Check the current round in the chamber"
                )
            ]
        )
        async def select_callback(self, select, interaction):
            match select.values[0]:
                case 'Shotgun':
                    if interaction.user != self.game.current_player.member:
                        await interaction.response.send_message("ain't your turn", ephemeral=True, delete_after=1.5)
                        return
                    if self.game.current_shell == len(self.game.shells):
                        await interaction.response.send_message("No shells left", ephemeral=True, delete_after=1.5)
                        return
                    view = Buckshot.ChooseShotgun()
                    view.game = self.game
                    await interaction.response.edit_message(view=view)
                case 'Beer':
                    if self.game.current_shell == len(self.game.shells):
                        await interaction.response.send_message("No shells left", ephemeral=True, delete_after=1.5)
                        return
                    if interaction.user != self.game.current_player.member:
                        await interaction.response.send_message("ain't your turn", ephemeral=True, delete_after=1.5)
                        return
                    if self.game.current_player.items['beer'] == 0:
                        await interaction.response.send_message("There is no beer in your inventory :1984:",
                                                                ephemeral=True, delete_after=1.5)
                        return
                    current_player_name = str(self.game.current_player.member.display_name)
                    used_shell_idx = int(self.game.current_shell)
                    used_shell = '▮ live round' if self.game.shells[self.game.current_shell] == 1 else '▯ blank'
                    self.game.use_beer()

                    game_content = self.game.generate_stats_message()
                    await interaction.response.edit_message(content=game_content, view=None, delete_after=1.5)
                    await interaction.followup.send(f"🍺 **{current_player_name}** drinks beer and removes "
                                                    f"a {used_shell} from the chamber", delete_after=5)
                    await asyncio.sleep(1)
                    await self.game.check_for_reload(interaction, used_shell_idx)

                case 'Handcuffs':
                    if interaction.user != self.game.current_player.member:
                        await interaction.response.send_message("ain't your turn", ephemeral=True, delete_after=1.5)
                        return
                    if self.game.current_player.items['handcuffs'] == 0:
                        await interaction.response.send_message("There is no handcuffs in your inventory :1984:",
                                                                ephemeral=True, delete_after=1.5)
                        return
                    if self.game.used_handcuffs:
                        await interaction.response.send_message("You have already used handcuffs this move",
                                                                ephemeral=True, delete_after=1.5)
                        return
                    self.game.use_handcuffs()
                    current_player_name = str(self.game.current_player.member.display_name)
                    current_opponent_name = str(self.game.current_opponent.member.display_name)

                    game_content = self.game.generate_stats_message()
                    await interaction.response.edit_message(content=game_content, view=None, delete_after=1.5)
                    await interaction.followup.send(
                        f"⛓ **{current_player_name}** handcuffed **{current_opponent_name}** "
                        f"(opponent skips the next turn)",
                        delete_after=5)
                    await asyncio.sleep(1)
                    await self.game.send_game_message(interaction)
                case 'Hand saw':
                    if interaction.user != self.game.current_player.member:
                        await interaction.response.send_message("ain't your turn", ephemeral=True, delete_after=1.5)
                        return
                    if self.game.current_player.items['saw'] == 0:
                        await interaction.response.send_message("There is no hand saw in your inventory :1984:",
                                                                ephemeral=True, delete_after=1.5)
                        return
                    if self.game.used_saw:
                        await interaction.response.send_message("You have already used a hand saw this move",
                                                                ephemeral=True, delete_after=1.5)
                        return
                    self.game.use_saw()
                    current_player_name = str(self.game.current_player.member.display_name)

                    game_content = self.game.generate_stats_message()
                    await interaction.response.edit_message(content=game_content, view=None, delete_after=1.5)
                    await interaction.followup.send(f"🔪 **{current_player_name}** sawed off the barrel (x2 damage)",
                                                    delete_after=5)
                    await asyncio.sleep(1)
                    await self.game.send_game_message(interaction)
                case 'Cigarette':
                    if interaction.user != self.game.current_player.member:
                        await interaction.response.send_message("ain't your turn", ephemeral=True, delete_after=1.5)
                        return
                    if self.game.current_player.items['cigarette'] == 0:
                        await interaction.response.send_message("There is no cigarette in your inventory :1984:",
                                                                ephemeral=True, delete_after=1.5)
                        return
                    await self.game.use_cigarette(interaction)
                    current_player_name = str(self.game.current_player.member.display_name)

                    game_content = self.game.generate_stats_message()
                    await interaction.response.edit_message(content=game_content, view=None, delete_after=1.5)
                    await interaction.followup.send(f"🚬 **{current_player_name}** smokes (regain 1 charge)",
                                                    delete_after=5)
                    await asyncio.sleep(1)
                    await self.game.send_game_message(interaction)
                case 'Magnifying glass':
                    if interaction.user != self.game.current_player.member:
                        await interaction.response.send_message("ain't your turn", ephemeral=True, delete_after=1.5)
                        return
                    if self.game.current_player.items['magnifying glass'] == 0:
                        await interaction.response.send_message("There is no magnifying glass in your inventory :1984:",
                                                                ephemeral=True, delete_after=1.5)
                        return
                    shell = self.game.use_magnifying_glass()
                    current_player_name = str(self.game.current_player.member.display_name)

                    game_content = self.game.generate_stats_message()
                    await interaction.response.edit_message(content=game_content, view=None, delete_after=1.5)
                    await interaction.followup.send(
                        f"🔍 **{current_player_name}** uses a magnifying glass and checks the current shell "
                        f"in the chamber", delete_after=5)
                    await interaction.followup.send(f"You see a {shell} in the shotgun chamber",
                                                    ephemeral=True, delete_after=5)
                    await asyncio.sleep(1)
                    await self.game.send_game_message(interaction)

        @discord.ui.button(label="debug", row=2, style=discord.ButtonStyle.blurple, emoji="👨‍💻")
        async def button_callback_debug(self, button, interaction):
            # allowed_users = ('694215003347091564', )
            # if interaction.user.id not in allowed_users:
            #     await interaction.response.send_message('nuh uh')
            #     return
            await interaction.response.defer()
            # print(self.game.current_player.member)
            # print(type(self.game.current_player.member))
            # print(self.game.current_opponent.member)
            # print(type(self.game.current_opponent.member))
            # print(f"{self.game.current_player.member.name}, {self.game.current_player.member.display_name},"
            #       f" {self.game.current_player.member.nick}")
            print(f"round: {self.game.current_round}")
            print(f"player: {self.game.current_player.member.display_name}, "
                  f"opponent: {self.game.current_opponent.member.display_name}")
            print(self.game.shells, self.game.current_shell)

    class ConfirmInvitation(discord.ui.View):
        def __init__(self):
            # super().__init__(timeout=60)
            super().__init__(disable_on_timeout=True)

        # async def on_timeout(self):
        #     self.disable_all_items()
        #     await self.message.edit(view=self)

        player1 = None
        player2 = None
        max_health = None
        game_mode = None

        @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green, emoji="✅")
        async def button_callback_confirm(self, button, interaction):
            if interaction.user != self.player2:
                await interaction.response.send_message("That is not your button", ephemeral=True)
                return
            await interaction.response.edit_message(view=None)  # remove "confirm" and "decline" buttons
            new_game = GameLogic(self.player1, self.player2, self.max_health, self.game_mode)
            new_game.new_round()
            view = Buckshot.ChooseAction()
            view.game = new_game

            # determine the first player
            content = "🪙 Flipping a coin"
            coin_message = await interaction.followup.send(content)  # send the coin message
            await asyncio.sleep(0.1)
            for i in range(3):
                content += '.'
                await interaction.followup.edit_message(coin_message.id, content=content)
                await asyncio.sleep(0.1)
            tmp = [new_game.player1, new_game.player2]
            random.shuffle(tmp)
            new_game.current_player, new_game.current_opponent = tmp
            content = f"🪙 **{new_game.current_player.member.display_name}** starts the game"
            await interaction.followup.edit_message(coin_message.id, content=content)
            await asyncio.sleep(1)

            # show shells
            seconds = 5
            shells = ''.join('▮' if bullet else '▯' for bullet in new_game.shells)
            content = (f"**ROUNDS (DISAPPEARS IN {seconds} SECONDS):**\n"
                       f"{shells}")
            shells_message = await interaction.followup.send(content=content)  # send shells message
            await asyncio.sleep(1)
            for seconds in range(seconds - 1, 0, -1):
                content = (f"**ROUNDS (DISAPPEARS IN {seconds} SECONDS):**\n"
                           f"{shells}")
                await interaction.followup.edit_message(shells_message.id, content=content)
                await asyncio.sleep(1)
            await interaction.followup.delete_message(shells_message.id)
            random.shuffle(new_game.shells)

            # start the game
            content = new_game.generate_stats_message()
            await interaction.followup.send(content=content, view=view)  # send game message

        @discord.ui.button(label="Decline", style=discord.ButtonStyle.red, emoji="<:red_crossmark:1138130077629042731>")
        async def button_callback_decline(self, button, interaction):
            if interaction.user != self.player2:
                await interaction.response.send_message("That is not your button", ephemeral=True)
                return
            await interaction.response.edit_message(view=None)
            await interaction.followup.send(content=f"**{self.player2.display_name}** declined")

    @discord.slash_command(
        name='buckshot-duel',
        description='A stolen game'
    )
    @option(name='player', description='Member you want to play with', required=True)
    @option(name='max_health', description='Max health for each player. Default is set to 6',
            default=6, min_value=1, max_value=15, required=False)
    @option(name='game_mode', description='gm', choices=['normal', 'cutoff'],
            default='normal', required=False)
    async def buckshot(self, ctx, opponent: discord.Member, max_health: int, game_mode: str):
        player1 = ctx.author
        player2 = opponent

        content = f'{player2.mention}, **{player1.display_name}** has invited you to play a game of buckshot roulette'
        alert_content = ""
        if game_mode == 'cutoff':
            if max_health != 6:
                max_health = 6
                alert_content = "Max health for this game mode must be 6, so your value got overriden"
            content += (f" (max health: **{max_health}**, game_mode: **{game_mode.upper()}**)\n"
                        f"{game_mode.upper()}: when you get to < 3 health, you cant recharge / "
                        f"use defibrillator no more (last life)")
        elif max_health != 6:
            content += f" (max health: **{max_health}**)"
        view = self.ConfirmInvitation()
        view.player1 = player1
        view.player2 = player2
        view.max_health = max_health
        view.game_mode = game_mode
        await ctx.respond(content, view=view)
        if alert_content:
            await ctx.followup.send(alert_content, ephemeral=True)


def setup(bot):
    bot.add_cog(Buckshot(bot))


"""
**player1**
▮▮▮▯
🔪x1 🔍x2 🍺x2 ⛓x1 🚬x1

**player2**
▮▮▯▯
🔪x0 🔍x1 🍺x3 ⛓x2 🚬x0


**rounds**
▮▯▮▮▯▯
"""
"""
f"**{self.player1.display_name}**\n"
"▮▮▮▯\n"
"🔪x1 🔍x2 🍺x2 ⛓x1 🚬x1\n\n"
f"**{self.player2.display_name}**\n"
"▮▮▯▯\n"
"🔪x0 🔍x1 🍺x3 ⛓x2 🚬x0\n\n"
"**ROUNDS:**\n"
"▮▯▮▮▯▯")
"""
