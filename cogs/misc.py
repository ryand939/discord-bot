# misc.py




import discord
from discord import Embed
from discord.ext import commands
import help
import util

from resources.misc.russian_roulette import RussianRoulette


class Misc(commands.Cog, description="Miscellaneous commands"):
    def __init__(self, bot):
        self.bot = bot
        # Initialize other necessary attributes here (e.g., bank, config)




    @commands.hybrid_group(name='misc')
    async def misc(self, ctx):
        if ctx.invoked_subcommand is None:
            await help.invoke_group_help(ctx.cog.walk_commands(), ctx)


    @misc.command(name="russianroulette", description="Russian roulette - 1/6 chance for 1hr timeout.", aliases=["rr"])
    @commands.cooldown(1, 30, commands.BucketType.member)
    async def rr(self, ctx):        
        if isinstance(ctx, discord.Interaction):
            await ctx.response.defer()
        russian_roulette = RussianRoulette(ctx)
        await russian_roulette.execute()


#    async def cog_command_error(self, ctx, error: Exception):
        #if isinstance(error, commands.CommandOnCooldown):
         #   await util.send_cooldown_alert(ctx, error=error, deleteAfter=8)
        #else:
         #   print(f"Unhandled error in guild {ctx.guild.id} for user {ctx.author.id}: {error}")
           





async def setup(client):
    await client.add_cog(Misc(client))