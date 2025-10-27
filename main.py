import discord
from discord import app_commands
from discord.ext import commands
from Components.VoteControl import VoteControl
import sqlite3

intents = discord.Intents.default()
intents.members = True
token = open("token.txt", "r").read().strip()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)


@tree.command(name="ping", description="Returns pong!")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")
    
@tree.command(name="voteregister", description="Send a register view") # Command to register in tier list voting
@commands.has_permissions(administrator=True)
async def voteregister(interaction: discord.Interaction):
    if interaction.channel.id in VoteControl.channel.keys():
        await interaction.response.send_message(
            "A registration is already active in this channel.",
            ephemeral=True
        )
        return
    
    
    voteControl = VoteControl(interaction.channel, interaction.user)
    await voteControl.start()

    VoteControl.channel[interaction.channel.id] = voteControl
    await interaction.response.send_message(
        "Registration started! Check your DMs for the control panel.",
        ephemeral=True
    )

    
@bot.event
async def on_ready():
    await tree.sync()
    print(f'We have logged in as {bot.user}')

bot.run(token)