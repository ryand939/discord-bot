import os
import discord
from help import invoke_group_help
from discord.ext import commands
from bank import Bank
from random import choice, randint
import asyncio
from config import BotConfig

class Gamble(commands.Cog, description="gambling commands"):


    def __init__(self, client):
        self.client = client
        self.bank = Bank()
        self.config = BotConfig("./resources/storage/gamble.json")




    @commands.hybrid_group(name='gamble')
    async def gamble(self, ctx):
        if ctx.invoked_subcommand is None:
            await invoke_group_help(ctx.cog.walk_commands(), ctx)
        


    @gamble.command(name="coinflip", description="Heads or tails.", aliases=["cf"])
    @commands.cooldown(1, 5, commands.BucketType.member)
    async def coinflip(self, ctx, side: str, bet: int):
        if not await self.is_gamble_channel(ctx): return
        elif ctx.interaction: await ctx.interaction.response.defer()
        
        # check input and confirm user has enough money to cover the bet
        if side.lower() not in ["t","tail","tails","h","head","heads"] or bet <= 0:
            return await ctx.send("Invalid input " + ctx.message.author.mention, delete_after=3)
        elif not self.bank.withdraw(ctx.guild.id, ctx.author.id, bet):
            return await ctx.send("Insufficient funds " + ctx.message.author.mention, delete_after=3)
            
        # determine side, send a coinflip gif and wait for it to play out
        randomNumber = randint(0,1)
        if randomNumber == 0: 
            await ctx.send(file=discord.File('./resources/gamble/coinflip/heads/' + 
            choice(os.listdir(os.getcwd() + "/resources/gamble/coinflip/heads/"))))
        else: 
            await ctx.send(file=discord.File('./resources/gamble/coinflip/tails/' + 
            choice(os.listdir(os.getcwd() + "/resources/gamble/coinflip/tails/"))))
        await asyncio.sleep(4) 

        # reveal results with a message
        if (randomNumber == 0 and side.lower()[0] == 'h') or (randomNumber == 1 and side.lower()[0] == 't'):
            self.bank.deposit(ctx.guild.id, ctx.author.id, bet*2)
            await ctx.send(ctx.message.author.mention + f" won {bet} daercoin!")
        else: 
            sideResult = "heads" if randomNumber == 0 else "tails"
            await ctx.send(ctx.message.author.mention + f" {sideResult}, unlucky!")

        
    
    @gamble.command(name="setchannel", description="Set gambling channel.", aliases=["channel"])
    @commands.has_permissions(administrator=True)
    async def setchannel(self, ctx, channel: discord.TextChannel):
        if ctx.interaction: await ctx.interaction.response.defer()

        # none if dne, channel id int if exist
        gambleChannel = self.config.get(str(ctx.guild.id), "gamblechannel")

        # if param is current gamble channel, remove
        if channel.id == gambleChannel:
            self.config.clear(str(ctx.guild.id),"gamblechannel")
            await ctx.send(f"Gambling commands will no longer be limited to {channel.id}.", delete_after=8)
        # if param is not current gamble channel, add
        else:
            self.config.set(str(ctx.guild.id), "gamblechannel", channel.id)
            await ctx.send(f"Successfully set gambling channel to {channel.id}. Gambling commands will not work anywhere else.", delete_after=8)


    # determines if a command was send from a registered gambling channel
    async def is_gamble_channel(self, ctx):
        gambleChannel = self.config.get(str(ctx.guild.id), "gamblechannel")

        # not correct gamble channel
        if gambleChannel != ctx.channel.id and gambleChannel is not None:
            await ctx.message.delete()
            cnl = await self.client.fetch_channel(gambleChannel)
            await ctx.send(f"Please use {cnl.mention} to gamble.", delete_after=6)
            return False
        else: 
            return True




    async def cog_command_error(self, ctx, error: Exception):
        if isinstance(error, commands.CommandOnCooldown):
            pass # delay is just to let the current game play out
        else:
            print(error)


async def setup(client):
    await client.add_cog(Gamble(client))
