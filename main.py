import discord
import os


client = discord.Client(intents=discord.Intents.all())
tree = discord.app_commands.CommandTree(client=client)


class JoinButton(discord.ui.Button):
    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.label = 'JOIN'
        self.style = discord.ButtonStyle.green
        self.interaction = interaction

    async def callback(self, interaction: discord.Interaction):
        if interaction.user in self.view.participants:
            await interaction.response.send_message(content='You already joined!', ephemeral=True)
        else:
            self.view.participants.append(interaction.user)
            content = '**ROCK-PAPER-SCISSORS**\n'

            content += '\n'.join([x.mention for x in self.view.participants])
            await self.interaction.edit_original_response(content=content)
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
            self.disabled = True
            view = RpsGameView(self.view.participants)
            await interaction.response.send_message(content='Choose:', view=view)


class RpsButton(discord.ui.Button):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(content=f'{interaction.user.name} just voted!')


class RpsGameView(discord.ui.View):
    def __init__(self, participants: list[discord.User]):
        super().__init__()
        self.vote_state = {p: 'X' for p in participants}
        self.add_item(RpsButton(label='ROCK', emoji='🪨'))
        self.add_item(RpsButton(label='PAPER', emoji='🧻'))
        self.add_item(RpsButton(label='SCISSORS', emoji='✂'))


class RpsJoinView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, *a, **kw):
        super().__init__(*a, **kw)
        self.author = interaction.user
        self.participants = [self.author]
        self.add_item(JoinButton(interaction=interaction))
        self.add_item(StartButton())


@tree.command(
    name='rps',
    description='Play rock-paper-scissors'
)
async def __command_rps(
        interaction: discord.Interaction
) -> None:
    view = RpsJoinView(interaction)
    await interaction.response.send_message(content=f'ROCK-PAPER-SCISSORS\n{interaction.user.mention}', view=view)


@client.event
async def on_ready():
    # await tree.sync()
    print('ready')


TOKEN = os.environ['TOKEN']
client.run(TOKEN)
