
import os
import discord
from discord import File
from discord.ext import commands
from random import choice, random
import math
import asyncio

from config import BotConfig
from resources.gamble.gamble_base import GambleGame 
import util


class Limbo(GambleGame):
    def __init__(self, ctx: commands.Context, bet: int, guess: float):
        """
        Initializes the Limbo game with the user's guess.

        :param ctx: The context of the command invocation.
        :param bet: The amount of daercoin bet by the user.
        :param guess: The user's guess that the bot will generate a higher number than this.
        """
        super().__init__(ctx, bet, 'limbo')
        self.guess = guess

    async def play(self):
        
        # validate the guess
        if not await self.validate_guess(self.guess, min_guess=1.0): return  
        # validate the bet range, no upper limit
        if not await self.validate_bet_range(min_amount=1, max_amount=None): return  
        # withdraw bet
        if not await self.attempt_withdraw_bet(): return  

        # generate a random value with a house edge on higher numbers
        random_value = random()
        final_random = round((((1 / random_value) * 0.90) if random_value < 0.25 else (1 / random_value)), 3)

        # prepare the initial embed
        gamble_embed = util.get_embed(None, None)
        gamble_embed.set_author(
            name=f"{self.author.display_name} bet {self.bet} daercoin with a guess of {self.guess}x",
            icon_url=self.author.avatar.url if self.author.avatar else None
        )
        gamble_embed.description = f"Guessing lower than the bot could win them `{math.floor(self.bet * self.guess)}` daercoin!"
        gamble_embed.set_footer(text=util.get_command_text(self.ctx))

        # send initial embed and have dramatic pause
        message = await self.ctx.send(embed=gamble_embed)
        await asyncio.sleep(6)

        # determine if the user won or lost
        if final_random >= self.guess:
            # case user wins
            winnings = math.floor(self.bet * self.guess)
            await self.payout(winnings)
            gamble_embed.color = util.success_green  # green color for win
            result_text = f"won {winnings} daercoin!"
        else:
            # case user loses
            gamble_embed.color = util.failure_red  # red color for loss
            result_text = f"lost {self.bet} daercoin!"

        # update embed with result
        gamble_embed.set_author(
            name=f"{self.author.display_name} {result_text}",
            icon_url=self.author.avatar.url if self.author.avatar else None
        )
        gamble_embed.description = (
            f"daerbot generated `{final_random}` and {self.author.name} guessed `{self.guess}`.\n"
            f"Leaving them with a balance of `{await self.bank.balance(self.ctx.guild.id, self.author.id)}` daercoin."
        )

        # edit original message with result new embed
        await message.edit(embed=gamble_embed, attachments=[])