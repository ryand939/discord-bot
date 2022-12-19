import discord
from help import invoke_group_help
import util
from discord.ext import commands, tasks
import datetime
import numpy as np
import asyncio

class Misc(commands.Cog, description="misc commands"):


    def __init__(self, client):
        self.client = client
        # preventing people from using roulette over and over
        self.rouletteTimeouts = []


    @commands.hybrid_group(name='misc')
    async def misc(self, ctx):
        if ctx.invoked_subcommand is None:
            await invoke_group_help(ctx.cog.walk_commands(), ctx)


    @misc.command(name="rr", description="Russian roulette - 1hr timeout.", aliases=["russianroulette"])
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def rr(self, ctx):
        if ctx.interaction: await ctx.interaction.response.defer()
        rng = np.random.default_rng()
        randomNumber = rng.integers(0, 6) + 1
        if randomNumber == 1:
            await ctx.send(file=discord.File("./resources/misc/media/rip.gif"))
            # pause for dramatic effect
            await asyncio.sleep(5) 
            # timeout for 1 hour
            await ctx.author.timeout(datetime.timedelta(hours=1), reason=f"You rolled {randomNumber}")
            await ctx.send(ctx.message.author.mention + f" has been timed out for 1 hour.")
        else:
            await ctx.send(ctx.message.author.mention + f" survived russian roulette! Random number = {randomNumber}")


    async def cog_command_error(self, ctx, error: Exception):
        if isinstance(error, commands.CommandOnCooldown):
            await util.send_cooldown_alert(ctx, error=error, deleteAfter=3)


async def setup(client):
    await client.add_cog(Misc(client))