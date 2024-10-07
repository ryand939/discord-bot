
import discord
from discord import File
from discord.ext import commands
from random import choice, random
import asyncio
import math
import os

from resources.gamble.gamble_base import GambleGame
from collectable import Item
import util


class CollectableGamble(GambleGame):
    def __init__(self, ctx: commands.Context, daercoin: int):
        """
        Initializes the CollectableGamble game with the bet amount.

        :param ctx: The context of the command invocation.
        :param daercoin: The daercoin amount to bet.
        """
        super().__init__(ctx, daercoin, 'collectable')
        self.daercoin = daercoin
        self.min_bet = 500
        self.max_bet = 2000

    async def play(self):

        # validate bet and withdraw
        if not await self.validate_bet_range(min_amount=self.min_bet, max_amount=self.max_bet): return 
        if not await self.attempt_withdraw_bet(): return  

        # calculate adjusted probabilities based on bet amount
        bet_fraction = (self.daercoin - self.min_bet) / (self.max_bet - self.min_bet) if self.max_bet != self.min_bet else 1

        # base probabilities at min and max bet
        probs_min = {'common': 0.63, 'uncommon': 0.20, 'rare': 0.10, 'legendary': 0.05, 'relic': 0.02}
        probs_max = {'common': 0.16, 'uncommon': 0.25, 'rare': 0.30, 'legendary': 0.21, 'relic': 0.08}

        # calc adjusted probabilities
        adjusted_probs = {}
        for rarity in probs_min:
            adjusted_probs[rarity] = probs_min[rarity] + (probs_max[rarity] - probs_min[rarity]) * bet_fraction

        # verify that the probabilities sum to 1
        total_prob = sum(adjusted_probs.values())
        adjusted_probs = {rarity: prob / total_prob for rarity, prob in adjusted_probs.items()}

        # Create cumulative probabilities for determining the obtained rarity
        cumulative_probs = []
        cumulative = 0.0
        for rarity in ['common', 'uncommon', 'rare', 'legendary', 'relic']:
            cumulative += adjusted_probs[rarity]
            cumulative_probs.append((rarity, cumulative))

        # determine the obtained rarity
        randomgen = random()
        obtained_rarity = None
        for rarity, cumulative_prob in cumulative_probs:
            if randomgen <= cumulative_prob:
                obtained_rarity = rarity
                break

        # fallback in case of any issue
        if obtained_rarity is None:
            obtained_rarity = 'common'

        # get all items and filter by rarity
        all_items = await self.bank.get_all_items()
        items_of_rarity = [item for item in all_items.values() if item.rarity.lower() == obtained_rarity]


        # select random item
        obtained_item = choice(items_of_rarity)

        # attempt to add item to user, record if success or fail
        added = await self.bank.add_item(self.ctx.guild.id, self.author.id, obtained_item.item_id)

        # build embed to show result
        embed, file = await self.bank.display_item(obtained_item.item_id, simple_display=True)
        embed.timestamp = discord.utils.utcnow()

        # get other info like items left to collect and display in footer
        total_items = len(all_items)
        user_items = await self.bank.get_inventory_strings(self.ctx.guild.id, self.author.id)
        owned_items = len(user_items)
        items_left = total_items - owned_items
        embed.set_footer(text=f"{self.author.display_name} has {items_left} items left to collect")

        # determine if the item is a dupe or new
        if not added:
            # case duplicate item :(
            embed.set_author(
                name=f"{self.author.display_name} received a duplicate collectable!",
                icon_url=self.author.avatar.url if self.author.avatar else None
            )
            embed.description = (
                f"{self.author.display_name}'s {self.daercoin} DC bet would have won them **{obtained_item.name}** "
                f"from the **{obtained_rarity}** tier, but they already own it. Better luck next time!"
            )
            embed.color = util.failure_red  # Red color for duplicate
        else:
            # case new item
            embed.set_author(
                name=f"{self.author.display_name} received a new collectable!",
                icon_url=self.author.avatar.url if self.author.avatar else None
            )
            embed.description = (
                f"{self.author.display_name}'s {self.daercoin} DC bet has won them **{obtained_item.name}** "
                f"from the **{obtained_rarity}** tier!"
            )
            embed.color = util.success_green  # Green color for success

        # done!!!!!
        await self.ctx.send(embed=embed, file=file)