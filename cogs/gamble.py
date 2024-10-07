# gamble.py

import os
import discord
import math
from help import invoke_group_help
from discord import app_commands
from discord.ext import commands
from bank import Bank
import asyncio
from config import BotConfig
from discord import Embed
from resources.gamble.coinflip.coinflip import Coinflip
from resources.gamble.collectable.gamble_collectable import CollectableGamble
from resources.gamble.limbo.limbo import Limbo

import util



class Gamble(commands.Cog, description="Gamble for items and daercoin"):

    def __init__(self, client):
        self.client = client
        self.bank = Bank()
        self.config = BotConfig(f"{util.bot_directory}resources/storage/gamble.json")



    async def before_gamble(self, ctx):
         # check if gambling channel
        if not await self.is_gamble_channel(ctx):
            raise commands.CheckFailure("Not gambling channel")
        if isinstance(ctx, discord.Interaction):
            await ctx.response.defer()



    @commands.hybrid_group(name='gamble')
    async def gamble_group(self, ctx):
        if ctx.invoked_subcommand is None:
            await invoke_group_help(ctx.cog.walk_commands(), ctx)



    @gamble_group.command(name="coinflip", description="Heads or tails.", aliases=["cf"])
    @commands.cooldown(1, 7, commands.BucketType.member)
    @commands.before_invoke(before_gamble)
    @app_commands.describe(side="Heads or tails. Accepts input 't', 'tail', 'tails', 'h', 'head', or 'heads'",
                           bet="Your daercoin bet. If you win, you will double your bet.")
    async def coinflip(self, ctx, side: str, bet: int):
        # instantiate and execute a Coinflip game
        coinflip = Coinflip(ctx, bet, side)
        await coinflip.flip()



    @gamble_group.command(name="limbo", description="Guess lower than bot!", aliases=["l"])
    @commands.cooldown(1, 7, commands.BucketType.member)
    @commands.before_invoke(before_gamble)
    @app_commands.describe(guess="Your random number guess >1.0. You want the bot to generate something HIGHER than this.",
                           bet="Your daercoin bet. If you win, you will receive {GUESS*BET} daercoin")
    async def limbo(self, ctx, guess: float, bet: int):
        # instantiate and execute a Limbo game
        limbo = Limbo(ctx, bet, guess)
        await limbo.play()



    @gamble_group.command(name="collectable", description="Gamble your daercoin for a collectable item!", aliases=["col"])
    @commands.before_invoke(before_gamble)
    @app_commands.describe(daercoin="Bet amount (500-2000 DC). Higher bets increase odds for rarer items.")
    async def collectable(self, ctx, daercoin: int):
        # instantiate and execute collectable gamble
        gamble_collectable = CollectableGamble(ctx, daercoin)
        await gamble_collectable.play()



    @gamble_group.command(name="stats", description="Game history.", aliases=["stat"])
    @commands.cooldown(1, 5, commands.BucketType.member)
    async def stats(self, ctx):
        headsNum = await self.config.get(str(ctx.guild.id), "heads")
        tailsNum = await self.config.get(str(ctx.guild.id), "tails")
        
        wins = await self.config.get(str(ctx.guild.id), "wins")
        losses = await self.config.get(str(ctx.guild.id), "losses")
        headsNum = 0 if headsNum is None else headsNum
        tailsNum = 0 if tailsNum is None else tailsNum
        output = f"Heads: {headsNum}\nTails: {tailsNum}\nWins: {wins}\nLosses: {losses}"
        await ctx.send(f"```{output}```")

    @gamble_group.command(name="setchannel", description="Set gambling channel.", aliases=["channel"])
    @commands.has_permissions(administrator=True)
    async def setchannel(self, ctx, channel: discord.TextChannel):
        # none if dne, channel id int if exist
        gambleChannel = await self.config.get(str(ctx.guild.id), "gamblechannel")

        # if param is current gamble channel, remove
        if channel.id == gambleChannel:
            await self.config.clear(str(ctx.guild.id),"gamblechannel")
            await ctx.send(f"Gambling commands will no longer be limited to {channel.id}.", delete_after=8)
        # if param is not current gamble channel, add
        else:
            await self.config.set(str(ctx.guild.id), "gamblechannel", channel.id)
            await ctx.send(f"Successfully set gambling channel to {channel.id}. Gambling commands will not work anywhere else.", delete_after=8)


    async def is_gamble_channel(self, ctx):
        gambleChannel = await self.config.get(str(ctx.guild.id), "gamblechannel")

        if gambleChannel != ctx.channel.id and gambleChannel is not None:
            cnl = self.client.get_channel(gambleChannel)
            if cnl:
                if not isinstance(ctx, discord.Interaction): await ctx.message.delete()
                title = "Error: Incorrect channel for gambling"
                description = f"Please use the {cnl.mention} channel to gamble."
                color = util.failure_red
                delete_after = 12
            else:
                title = "Warning: Gambling channel could not be found."
                description = "The gambling channel for this server has been assigned, but the channel itself has likely been deleted. Daerbot will disregard this nonexistent channel going forward and allow gambling everywhere."
                await self.config.clear(str(ctx.guild.id),"gamblechannel")
                color = util.warning_yellow
                delete_after = None

            embed = discord.Embed(description=description, color=color, timestamp=discord.utils.utcnow())
            embed.set_author(name=title, icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
            embed.set_footer(text=util.get_command_text(ctx) )
            await ctx.send(embed=embed, delete_after=delete_after)

            return False
        return True


    
    async def cog_command_error(self, ctx, error: Exception):
        if isinstance(error, commands.CommandOnCooldown):
            pass
            #await util.send_cooldown_alert(ctx, error=error, deleteAfter=5)
        elif isinstance(error, commands.CheckFailure):
            # The error message is already sent in 'is_gamble_channel'
            pass
        else:
            print(f"Unhandled error in guild {ctx.guild.id} for user {ctx.author.id}: {error}")




async def setup(client):
    await client.add_cog(Gamble(client))
