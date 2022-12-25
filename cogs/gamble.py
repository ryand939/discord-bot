import os
import discord
from help import invoke_group_help
from discord.ext import commands
from bank import Bank
from random import choice, randint
import asyncio

class Gamble(commands.Cog, description="gambling commands"):


    def __init__(self, client):
        self.client = client
        self.bank = Bank()




    @commands.hybrid_group(name='gamble')
    async def gamble(self, ctx):
        if ctx.invoked_subcommand is None:
            await invoke_group_help(ctx.cog.walk_commands(), ctx)


    @gamble.command(name="coinflip", description="Heads or tails.", aliases=["cf"])
    @commands.cooldown(1, 5, commands.BucketType.member)
    async def coinflip(self, ctx, side: str, bet: int):
        if ctx.interaction: await ctx.interaction.response.defer()
        
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

        



    async def cog_command_error(self, ctx, error: Exception):
        if isinstance(error, commands.CommandOnCooldown):
            pass # delay is just to let the current game play out
        else:
            print(error)


async def setup(client):
    await client.add_cog(Gamble(client))
