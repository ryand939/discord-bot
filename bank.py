# bank.py

from config import BotConfig
from util import bot_directory
from collectable import load_items
import discord
import os 
from collectablestats import CollectionStats
import asyncio

class Bank:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Bank, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.bank = BotConfig(f"{bot_directory}resources/storage/economy.json")
        self.items = load_items(f"{bot_directory}resources/storage/items.json")
        self.collectable_log = CollectionStats(f"{bot_directory}resources/storage/collectable_log.json")
        self.lock = asyncio.Lock()
        self._initialized = True

    # --- methods relating to user balance ---

    async def withdraw(self, guildID, userID, amount):
        async with self.lock:
            balance = await self.bank.get(str(guildID), str(userID))
            if balance is None or (balance - amount) < 0:
                return False
            else:
                # Has enough balance
                await self.bank.set(str(guildID), str(userID), -amount, relative=True)
                return True

    async def deposit(self, guildID, userID, amount):
        async with self.lock:
            await self.bank.set(str(guildID), str(userID), amount, relative=True)

    async def balance(self, guildID, userID):
        async with self.lock:
            balance = await self.bank.get(str(guildID), str(userID))
            if balance is None:
                balance = 0
            return balance


    async def remove(self, guildID, userID):
        async with self.lock:
            await self.bank.clear(str(guildID), str(userID))
            await self.bank.clear_inventory(str(guildID), str(userID))

    async def leaderboard(self, guildID):
        async with self.lock:
            return await self.bank.get_list(str(guildID), sort=True)

    # --- methods relating to inventory collectables ---

    # returns a dictionary of items with item_id as keys and Item instances as values
    async def get_all_items(self):
        async with self.lock:
            return self.items

    # check if an item exists
    # returns true if item exists, false otherwise
    async def item_exists(self, item_id):
        async with self.lock:
            if item_id in self.items:
                return True
            else:
                return False

    # returns true if item was added to user inventory, false otherwise
    async def add_item(self, guildID, userID, item_id):
        async with self.lock:
            # ensure the item exists
            if item_id not in self.items:
                return False
            # add item to user inventory
            added = await self.bank.add_to_inventory(str(guildID), str(userID), item_id)
            # if successfully added, add userid to the owner list for item
            if added:
                await self.collectable_log.add_user_to_item(str(guildID), item_id, str(userID))
            return added

    # returns true if item was successfully removed from user inventory, false otherwise
    async def remove_item(self, guildID, userID, item_id):
        async with self.lock:
            # remove item from user inventory
            removed = await self.bank.remove_from_inventory(str(guildID), str(userID), item_id)
            # if successfully removed, remove userid from the owner list for item
            if removed:
                await self.collectable_log.remove_user_from_item(str(guildID), item_id, str(userID))
            return removed

    # returns true if an item id is found in user inventory, false otherwise
    async def has_item(self, guildID, userID, item_id):
        async with self.lock:
            inventory = await self.bank.get_inventory(str(guildID), str(userID))
            return item_id in inventory

    # returns list of item objects in the user's inventory
    async def get_inventory_items(self, guildID, userID):
        async with self.lock:
            item_ids = await self.bank.get_inventory(str(guildID), str(userID))
            return [self.items[item_id] for item_id in item_ids if item_id in self.items]
        
    # returns list of item_id strings that represent the users inventory
    async def get_inventory_strings(self, guildID, userID):
        async with self.lock:
            return await self.bank.get_inventory(str(guildID), str(userID))


    # clears every item out of a user's inventory
    # returns true if success, false otherwise
    async def clear_inventory(self, guildID, userID):
        async with self.lock:
            return await self.bank.clear_inventory(str(guildID), str(userID))
        
                
    async def display_item(self, item_id, simple_display=False):
        async with self.lock:
            item = self.items.get(item_id)

            # set embed color based on rarity
            rarity_colors = {
                'common': discord.Color.brand_green(),
                'uncommon': discord.Color.yellow(),
                'rare': discord.Color.blurple(),
                'legendary': discord.Color.orange(),
                'relic': discord.Color.brand_red()
            }
            color = rarity_colors.get(item.rarity.lower(), discord.Color.blue())

            # create the embed with item details
            embed = discord.Embed(
                title=item.name,
                description=item.description,
                color=color
            )

            # simple_display flag stuff
            if not simple_display:
                embed.add_field(name="ID", value=f"`{item_id}`", inline=True)
                embed.add_field(name="Class", value=item.itemclass.capitalize(), inline=True)
                embed.add_field(name="Rarity", value=item.rarity.capitalize(), inline=True)

                attributes = []
                if getattr(item, 'smokeable', False): attributes.append('smokeable')
                if getattr(item, 'snortable', False): attributes.append('snortable')
                if getattr(item, 'injectable', False): attributes.append('injectable')
                if getattr(item, 'edible', False): attributes.append('edible')
                if attributes:
                    embed.add_field(name="Special Attributes", value=", ".join(attributes), inline=False)

            item_image_filename = f"{item_id}.png"
            item_image_path = os.path.join(bot_directory, "resources", "collectables", "thumbnails", item_image_filename)

            # use default image if item's image does not exist
            if os.path.isfile(item_image_path):
                image_filename = item_image_filename
            else:
                image_filename = "unknown.png"

            # path to item image or default image
            image_path = os.path.join(bot_directory, "resources", "collectables", "thumbnails", image_filename)

            # set image for embed
            file = discord.File(image_path, filename=image_filename)
            embed.set_thumbnail(url=f"attachment://{image_filename}")

            return embed, file