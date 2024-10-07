# coinflip.py
import os
import discord
from discord import File
from discord.ext import commands
from random import choice, randint
import asyncio
from config import BotConfig
from resources.gamble.gamble_base import GambleGame
import util

class Coinflip(GambleGame):
    def __init__(self, ctx: commands.Context, bet: int, side: str): 
        super().__init__(ctx, bet, 'coinflip')
        self.side = side.lower()
        self.config = BotConfig(f"{util.bot_directory}resources/storage/gamble.json")

    async def flip(self):

        # validate all input and withdraw
        valid_sides = ["t", "tail", "tails", "h", "head", "heads"]
        if not await self.validate_input(self.side, valid_sides): return  
        if not await self.validate_bet_range(min_amount=1, max_amount=None): return  
        if not await self.attempt_withdraw_bet(): return  

        # normalize side guess
        side_guess = "heads" if self.side.startswith('h') else "tails"

        # outcome 0 for heads, 1 for tails
        random_number = randint(0, 1)
        side_result = "heads" if random_number == 0 else "tails"

        # random gif based on the outcome
        attachment_dir = os.path.join(util.bot_directory, "resources", "gamble", "coinflip", side_result)
        if not os.path.exists(attachment_dir):
            await self.send_embed(
                title="Couldn't find directory", 
                description="The coinflip resource directory was not found.",
                embed_type="fatal",
                delete_after=5
            )
            return

        try:
            attachment_file = choice(os.listdir(attachment_dir))
        except IndexError:
            await self.send_embed(
                title="Couldn't get GIF",
                description=f"There were no GIFs found in the `coinflip\\{side_result}` directory.",
                embed_type="fatal",
                delete_after=5
            )
            return

        attachment_path = os.path.join(attachment_dir, attachment_file)
        attachment = File(attachment_path, filename="coinflip.gif")

        # prepare the initial embed with the coinflip animation
        gamble_embed = util.get_embed(title=None, content=None, attachment="attachment://coinflip.gif")
        gamble_embed.set_author(
            name=f"{self.author.display_name} bet {self.bet} daercoin on {side_guess}!",
            icon_url=self.author.avatar.url if self.author.avatar else None
        )
        gamble_embed.set_footer(text=f"{self.author.display_name} could win {self.bet * 2} daercoin!")

        # send the initial embed with the GIF
        message = await self.ctx.send(file=attachment, embed=gamble_embed)
        await asyncio.sleep(6)  # Wait for the GIF to play out

        # determine if user won or lost
        if (random_number == 0 and side_guess == 'heads') or (random_number == 1 and side_guess == 'tails'):
            # case user wins
            await self.payout(self.bet * 2)
            gamble_embed.color = util.success_green  # Green color for win
            result_text = f"won {self.bet} daercoin on {side_guess}!"
            await self.config.set(str(self.ctx.guild.id), "wins", 1, relative=True)
        else:
            # case user loses
            gamble_embed.color = util.failure_red  # Red color for loss
            result_text = f"lost {self.bet} daercoin on {side_guess}!"
            await self.config.set(str(self.ctx.guild.id), "losses", 1, relative=True)

        # update the embed with the result
        gamble_embed.set_author(
            name=f"{self.author.display_name} {result_text}",
            icon_url=self.author.avatar.url if self.author.avatar else None
        )
        gamble_embed.description = f"Leaving them with a balance of `{await self.bank.balance(self.ctx.guild.id, self.author.id)}` daercoin."
        gamble_embed.set_image(url=None)  # remove original gif
        gamble_embed.set_footer(text=util.get_command_text(self.ctx))

        # edit the original message with the result
        await message.edit(embed=gamble_embed, attachments=[])