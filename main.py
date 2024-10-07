# main.py

import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
from help import CustomHelpCommand
from on_message import handle_on_message
from util import prefix, bot_directory

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


client = commands.Bot(command_prefix = prefix, 
                      intents        = discord.Intents.all(), 
                      help_command   = CustomHelpCommand(),
                      activity       = discord.Activity(type=discord.ActivityType.watching, name=f"for {prefix}"))


@client.event
async def on_ready():
    
    print(f"[STARTUP] {os.listdir()}")
    print(f"[STARTUP] {client.user} in server:")
    for index, guild in enumerate(client.guilds):
        print(f"[{index+1}] {guild.name}")
        
    for filename in os.listdir(f"{bot_directory}cogs"):
        if filename.endswith(".py"):
            await client.load_extension(f'cogs.{filename[:-3]}')

    cmd = await client.tree.sync()
    print(f"Synced {len(cmd)} slash commands")
    

 
@client.event
async def on_message(message):

    # dont take commands from bots
    if message.author.bot: return

    # perform action on any user message
    await handle_on_message(client, message) 
    
    # now process command if there is any
    await client.process_commands(message)   
            

client.run(TOKEN)
