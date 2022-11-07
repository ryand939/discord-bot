import os
import discord
from help import invoke_group_help
import util
from discord.ext import commands
import datetime
from itertools import cycle
from resources.priv9.priv9_dev_schedule import Task
from discord import Embed


class Priv9(commands.Cog, description="priv9 commands"):


    def __init__(self, cli):
        self.cli = cli
        # load the priv9 ads
        adList = []
        for file in os.listdir("./resources/priv9/ad_media"):
            if file.endswith(".gif"):
                adList.append(file)
        self.imgPool = cycle(adList)
        self.devTask = Task()




    @commands.group(name='priv9')
    async def priv9(self, ctx):
        if ctx.invoked_subcommand is None:
            await invoke_group_help(ctx.cog.walk_commands(), ctx)


    @priv9.command(name="eta", description="Time until priv9 drops.")
    async def eta(self, ctx):
        releaseDate = datetime.datetime(2022, 11, 24) - datetime.datetime.now()
        minutes = releaseDate.seconds // 60
        hours = minutes // 60
        minutes = minutes % 60
        seconds = releaseDate.seconds % 60
        send = f"Priv9 will release in {releaseDate.days} days, {hours} hours, {minutes} minutes, and {seconds} seconds"
        await ctx.send(send)


    @priv9.command(name="ad", description="Send the next priv9 ad.")
    async def ad(self, ctx):
        path = f"./resources/priv9/ad_media/{next(self.imgPool)}"
        await ctx.send(file=discord.File(path))


    @priv9.command(name="status", description="Track priv9 dev activity.")
    async def status(self, ctx, footer=None):
        status, desc, time = self.devTask.get_current_task()
        gameEmbed = Embed(title=f"PRIV9 DEV STATUS: {status}", description=desc, color=0x3897f0)
        if footer == "-n":
            gameEmbed.set_footer(text=f"Next task in {int(time)} minutes")

        await ctx.send(embed=gameEmbed)


async def setup(client):
    await client.add_cog(Priv9(client))
