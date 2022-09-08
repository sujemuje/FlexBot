import random
from typing import *
import discord
import json
import os


client = discord.Client(intents=discord.Intents.all())
tree = discord.app_commands.CommandTree(client=client)


@tree.command(
    name='embed',
    description='embed'
)
async def __command_print(interaction: discord.Interaction, attachment: discord.Attachment):
    embed = discord.Embed.from_dict(
        json.loads((await attachment.to_file()).fp.read().decode('utf-8'))
    )
    await interaction.response.send_message(embed=embed)


@tree.command(
    name='message',
    description='message'
)
async def __command_embed(interaction: discord.Interaction, attachment: discord.Attachment):
    content = (await attachment.to_file()).fp.read().decode('utf-8')
    await interaction.response.send_message(content=content)


class JoinButton(discord.ui.Button):
    def __init__(self):
        super().__init__()
        self.label = 'JOIN'
        self.style = discord.ButtonStyle.green

    async def callback(self, interaction: discord.Interaction):
        if interaction.user in self.view.participants:
            await interaction.response.send_message(content='You already joined!', ephemeral=True)
        else:
            self.view.participants.append(interaction.user)
            content = interaction.message.content + '\n' + interaction.user.mention
            await interaction.response.edit_message(content=content)
            await interaction.response.send_message(content='Yo', ephemeral=True)


class StartButton(discord.ui.Button):
    def __init__(self):
        super().__init__()
        self.label = 'START'
        self.style = discord.ButtonStyle.blurple

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.view.participants[0]:
            await interaction.response.send_message(content='Only creator can start the game!', ephemeral=True)
        else:
            view = RpsGameView(self.view.participants)
            await interaction.response.edit_message(content=view.update_content(shadow=True), view=view)


class RpsButton(discord.ui.Button):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)

    async def callback(self, interaction: discord.Interaction):
        v = self.view.vote_state
        if v[interaction.user] != 'X':
            await interaction.response.send_message(content='You already voted!', ephemeral=True)
        else:
            v[interaction.user] = self.label[0]
            vv = v.values()
            if 'X' not in vv:
                content = self.view.update_content(shadow=False)
                content += '---------------------\n'
                if 'R' in vv and 'P' in vv and 'S' in vv or 'R' not in vv and 'P' not in vv or 'R' not in vv and 'S' not in vv or 'S' not in vv and 'P' not in vv:
                    content += '**DRAW!**'
                else:
                    content += '**RESULTS:**'
                    vi = v.items()
                    if 'R' not in vv:
                        for k, v in vi:
                            if v == 'S':
                                content += '\n' + k.mention
                    if 'P' not in vv:
                        for k, v in vi:
                            if v == 'R':
                                content += '\n' + k.mention
                    if 'S' not in vv:
                        for k, v in vi:
                            if v == 'P':
                                content += '\n' + k.mention
                await interaction.response.edit_message(content=content, view=None)
            else:
                content = self.view.update_content(shadow=True)
                await interaction.response.edit_message(content=content)


class RpsGameView(discord.ui.View):
    def __init__(self, participants: list[discord.User]):
        super().__init__()
        self.vote_state = {p: 'X' for p in participants}
        self.emotes = {
            'R': '🪨',
            'P': '🧻',
            'S': '✂'
        }
        self.add_item(RpsButton(label='ROCK', emoji=self.emotes['R']))
        self.add_item(RpsButton(label='PAPER', emoji=self.emotes['P']))
        self.add_item(RpsButton(label='SCISSORS', emoji=self.emotes['S']))

    def update_content(self, shadow: bool) -> str:
        content = '**CHOOSE:**\n'
        if shadow:
            for p, v in self.vote_state.items():
                content += p.mention + (' ❌\n' if v == 'X' else ' ✅\n')
            return content
        else:
            for p, v in self.vote_state.items():
                content += p.mention + (' ❌\n' if v == 'X' else f' {self.emotes[v]}\n')
            return content


class RpsJoinView(discord.ui.View):
    def __init__(self, author: discord.Member, *a, **kw):
        super().__init__(*a, **kw)
        self.author = author
        self.participants = [self.author]
        self.add_item(JoinButton())
        self.add_item(StartButton())


@tree.command(
    name='rps',
    description='Play rock-paper-scissors'
)
async def __command_rps(
        interaction: discord.Interaction
) -> None:
    view = RpsJoinView(interaction.user)
    await interaction.response.send_message(content=f'**ROCK-PAPER-SCISSORS**\n{interaction.user.mention}', view=view)


Coin = Literal['heads', 'tails']


@tree.command(
    name='coinflip',
    description='Flip a coin!'
)
async def __command_coinflip(
        interaction: discord.Interaction,
        bet: Coin
) -> None:
    coin = random.choice(['heads', 'tails'])
    content = f"It's a {coin}! You "
    if coin == bet:
        content += 'won!'
    else:
        content += 'lost!'
    await interaction.response.send_message(content=content)


@client.event
async def on_ready():
    await tree.sync()
    print('ready')


TOKEN = os.environ['TOKEN']
client.run(TOKEN)
