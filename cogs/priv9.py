import os
import discord
from help import invoke_group_help
import util
from discord.ext import commands
import datetime


class Priv9(commands.Cog, description="priv9 commands"):


    def __init__(self, cli):
        self.cli = cli
        # load the priv9 ads
        self.adList = []
        self.index = 0
        for file in os.listdir("./resources/priv9"):
            if file.endswith(".gif"):
                self.adList.append(file)



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
        # a circular linked list would be really nice here
        #
        # TODO: IMPLEMENT LINKED LIST!!

        if self.index >= len(self.adList):
            self.index = 0
        path = f"./resources/priv9/{self.adList[self.index]}"
        self.index += 1
        await ctx.send(file=discord.File(path))


async def setup(client):
    await client.add_cog(Priv9(client))