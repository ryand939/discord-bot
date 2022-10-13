import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
from help import CustomHelpCommand

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = commands.Bot(command_prefix='##', intents=discord.Intents.all(), help_command=CustomHelpCommand())


@client.event
async def on_ready():
    for guild in client.guilds:
        print(f"{client.user} in server {guild.name}")

    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await client.load_extension(f'cogs.{filename[:-3]}')
            

client.run(TOKEN)
