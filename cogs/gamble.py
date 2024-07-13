import os
import discord
import math
from help import invoke_group_help
from discord.ext import commands
from bank import Bank
from random import choice, randint, random
import asyncio
from config import BotConfig
from discord import Embed

import util




class Gamble(commands.Cog, description="gambling commands"):


    def __init__(self, client):
        self.client = client
        self.bank = Bank()
        self.config = BotConfig(f"{util.bot_directory}resources/storage/gamble.json")




    @commands.hybrid_group(name='gamble')
    async def gamble(self, ctx):
        if ctx.invoked_subcommand is None:
            await invoke_group_help(ctx.cog.walk_commands(), ctx)
        


    @gamble.command(name="coinflip", description="Heads or tails.", aliases=["cf"])
    @commands.cooldown(1, 7, commands.BucketType.member)
    async def coinflip(self, ctx, side: str, bet: int):
        if not await self.is_gamble_channel(ctx): return
        elif ctx.interaction: await ctx.interaction.response.defer()
        
        # check input and confirm user has enough money to cover the bet
        if side.lower() not in ["t","tail","tails","h","head","heads"] or bet <= 0:
            return await ctx.send("Invalid input " + ctx.message.author.mention, delete_after=3)
        elif not self.bank.withdraw(ctx.guild.id, ctx.author.id, bet):
            return await ctx.send("Insufficient funds " + ctx.message.author.mention, delete_after=3)
        
        sideGuess = side
        if side.lower() == "h" or side.lower() == "head": sideGuess = "heads"
        elif side.lower() == "t" or side.lower() == "tail": sideGuess = "tails"


        # determine side, send a coinflip gif and wait for it to play out
        randomNumber = randint(0,1)
        if randomNumber == 0: 

            attachment = discord.File(f'./resources/gamble/coinflip/heads/' + 
            choice(os.listdir(os.getcwd() + f"/resources/gamble/coinflip/heads/")), filename = "gif.gif")
        else: 
            attachment = discord.File(f"./resources/gamble/coinflip/tails/" + 
            choice(os.listdir(os.getcwd() + f"/resources/gamble/coinflip/tails/")), filename = "gif.gif")
        
        gamble_embed = util.get_embed(f"Coinflip: {ctx.message.author.name} bet {bet} daercoin on {sideGuess}!", None)
        gamble_embed.set_image(url="attachment://gif.gif")
        message = await ctx.send(file=attachment, embed=gamble_embed)

        await asyncio.sleep(6) 
        sideResult = "heads" if randomNumber == 0 else "tails"
        self.config.set(str(ctx.guild.id), sideResult, 1, True)

        # reveal results with a message

        # IF THEY WIN
        if (randomNumber == 0 and side.lower()[0] == 'h') or (randomNumber == 1 and side.lower()[0] == 't'):
            self.bank.deposit(ctx.guild.id, ctx.author.id, bet*2)
            gamble_embed.title = f"Coinflip: {ctx.message.author.name} won {bet} daercoin!"
            gamble_embed.colour=0x00e600 #GREEN WIN COLOUR
            self.config.set(str(ctx.guild.id), "wins", 1, True)

        # IF THEY LOSE
        else: 
            gamble_embed.title = f"Coinflip: {ctx.message.author.name} lost {bet} daercoin!"
            gamble_embed.colour=0xe60000 #RED LOSS COLOUR
            self.config.set(str(ctx.guild.id), "losses", 1, True)

        gamble_embed.set_image(url=None)
        gamble_embed.description = f"Leaving them with a balance of {self.bank.balance(ctx.guild.id, ctx.author.id)} daercoin"
        await message.delete()
        await ctx.send(embed=gamble_embed)
            

    @gamble.command(name="stats", description="Game history.", aliases=["stat"])
    @commands.cooldown(1, 5, commands.BucketType.member)
    async def stats(self, ctx):
        if ctx.interaction: await ctx.interaction.response.defer()

        headsNum = self.config.get(str(ctx.guild.id), "heads")
        tailsNum = self.config.get(str(ctx.guild.id), "tails")
        
        wins = self.config.get(str(ctx.guild.id), "wins")
        losses = self.config.get(str(ctx.guild.id), "losses")
        headsNum = 0 if headsNum is None else headsNum
        tailsNum = 0 if tailsNum is None else tailsNum
        output = f"Heads: {headsNum}\nTails: {tailsNum}\nWins: {wins}\nLosses: {losses}"
        await ctx.send(f"```{output}```")


    @gamble.command(name="limbo", description="Guess lower than bot!", aliases=["l"])
    @commands.cooldown(1, 6, commands.BucketType.member)
    async def limbo(self, ctx, guess: float, bet: int):
        if not await self.is_gamble_channel(ctx): return
        elif ctx.interaction: await ctx.interaction.response.defer()
        

        # check input and confirm user has enough money to cover the bet
        if guess <= 1: 
            return await ctx.send(f"Invalid input {ctx.message.author.mention}. Guess must be above 1.0.", delete_after=3)
        elif bet <= 0:
            return await ctx.send(f"Invalid input {ctx.message.author.mention}.", delete_after=3)
        elif not self.bank.withdraw(ctx.guild.id, ctx.author.id, bet):
            return await ctx.send("Insufficient funds " + ctx.message.author.mention, delete_after=3)
            
        randomValue = random()
        chance = (1 / guess)

        gamble_embed = util.get_embed(f"Limbo: {ctx.message.author.name} bet {bet} daercoin with a guess of {guess}x", None)
        gamble_embed.description = f"Guessing lower than the bot could win them {math.floor(bet * guess)} daercoin!"
        
        message = await ctx.send(embed=gamble_embed)
        await asyncio.sleep(5) 
        # insane house edge because i dont want people getting rich. im evil and i want people to lose muahahahaha
        if randomValue <= (chance - (chance * 0.11)):
            
            gamble_embed.title = f"Limbo: {ctx.message.author.name} won {math.floor(bet * guess)} daercoin!"
            self.bank.deposit(ctx.guild.id, ctx.author.id, math.floor(bet * guess))
            gamble_embed.description = f"daerbot generated {round((1 / randomValue), 3)} and {ctx.message.author.name} guessed {guess}! \nLeaving them with a balance of {self.bank.balance(ctx.guild.id, ctx.author.id)} daercoin"
            gamble_embed.colour=0x00e600 #GREEN WIN COLOUR
        else:
            gamble_embed.title = f"Limbo: {ctx.message.author.name} lost {bet} daercoin!"
            gamble_embed.description = f"daerbot generated {round((1 / randomValue), 3)} and {ctx.message.author.name} guessed {guess}. \nLeaving them with a balance of {self.bank.balance(ctx.guild.id, ctx.author.id)} daercoin"
            gamble_embed.colour=0xe60000 #RED LOSS COLOUR

        await message.edit(embed=gamble_embed)






    
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
