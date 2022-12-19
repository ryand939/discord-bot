import os
import discord
from help import invoke_group_help
from discord.ext import commands
from bank import Bank
import numpy as np
import random
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
            await ctx.send("Invalid input " + ctx.message.author.mention, delete_after=3)
            return
        elif not self.bank.withdraw(ctx.guild.id, ctx.author.id, bet):
            await ctx.send("Insufficient funds " + ctx.message.author.mention, delete_after=3)
            return

        randomNumber = random.randint(0,1)

        # send a conflip gif
        if randomNumber == 0:
            await ctx.send(file=discord.File('./resources/gamble/coinflip/heads/' + 
                random.choice(os.listdir(os.getcwd() + "/resources/gamble/coinflip/heads/"))))
            sideResult = 'heads'
        else:
            await ctx.send(file=discord.File('./resources/gamble/coinflip/tails/' + 
                random.choice(os.listdir(os.getcwd() + "/resources/gamble/coinflip/tails/"))))
            sideResult = 'tails'

        # delay to let the gif play out, and reveal results with a message
        await asyncio.sleep(4) 
        if (randomNumber == 0 and side.lower()[0] == 'h') or (randomNumber == 1 and side.lower()[0] == 't'):
            self.bank.deposit(ctx.guild.id, ctx.author.id, bet*2)
            await ctx.send(ctx.message.author.mention + f" won {bet} daercoin!")
        else: await ctx.send(ctx.message.author.mention + f" {sideResult}, unlucky!")

        



    async def cog_command_error(self, ctx, error: Exception):
        if isinstance(error, commands.CommandOnCooldown):
            pass # delay is just to let the current game play out


async def setup(client):
    await client.add_cog(Gamble(client))
