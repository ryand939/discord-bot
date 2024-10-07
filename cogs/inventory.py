# inventory.py

import discord
from help import invoke_group_help
from discord import app_commands
from discord.ext import commands
from bank import Bank
from collectable import Item



class Inventory(commands.Cog, description="view and manage your inventory of collectables."):


    def __init__(self, client):
        self.client = client
        self.bank = Bank()

    @commands.hybrid_group(name='collectable', aliases=["col", "c", "collect", "collection"])
    async def collectable(self, ctx):
        if ctx.invoked_subcommand is None:
            await invoke_group_help(ctx.cog.walk_commands(), ctx)


    @collectable.command(name="lookup", description="Look up a collectable item.")
    @app_commands.describe(who_owns="Show who owns this item (Enter 'true', 'yes', '1', 'y', 'who', or 't' to enable).")
    async def lookup(self, ctx, item_id: str, who_owns: str = "false"):
        
        who_owns = who_owns.lower() in ['who', 'true', 'yes', '1', 'y', 't']

        item_exists = await self.bank.item_exists(item_id)
        if item_exists:
            embed, file = await self.bank.display_item(item_id)
            if who_owns:
                # Get the list of user IDs who own the item in the current server
                user_ids = await self.bank.collectable_log.get_users_for_item(str(ctx.guild.id), item_id)
                # Convert user IDs to member objects
                members = [ctx.guild.get_member(int(user_id)) for user_id in user_ids if ctx.guild.get_member(int(user_id)) is not None]
                # Get the display names of the members
                member_names = [member.display_name for member in members]
                # Add a field to the embed
                number_of_owners = await self.bank.collectable_log.count_users_for_item(str(ctx.guild.id), item_id)
                if member_names:
                    value = ", ".join(member_names)
                    embed.set_footer(text=f'Owners ({number_of_owners}): {value}')
                else:
                    embed.set_footer(text=f'Owners ({number_of_owners}): No one owns this collectable item!')
        else:
            embed = discord.Embed(
                title="Invalid Collectable ID",
                description=f"The collectable with ID `{item_id}` does not exist.",
                color=discord.Color.red())
            embed.set_footer(text='Use ">collectable idlist" for a list of valid collectable IDs.')
            file = None

        await ctx.send(embed=embed, file=file)



    @collectable.command(name="inventory", description="Show the inventory of a user.", aliases=["inv", "i", "invent"])
    @app_commands.describe(show_missing="Include items the user doesn't have (enter 'true', 'yes', '1', 'y', or 't' to enable).",
                           tier="Filter items by rarity tier (enter 'relic', 'legendary', 'rare', 'uncommon', or 'common').",
                           user="The user whose inventory to display. Defaults to yourself.")
    async def inventory(self, ctx, user: discord.Member = None, show_missing: str = "false", tier: str = None):
        if user is None:
            user = ctx.author

        # Define rarity order and display names
        rarity_order = ['relic', 'legendary', 'rare', 'uncommon', 'common']
        rarity_display_names = {
            'relic': 'Relic',
            'legendary': 'Legendary',
            'rare': 'Rare',
            'uncommon': 'Uncommon',
            'common': 'Common'
        }

        # Parse and validate show_missing
        show_missing = show_missing.lower() in ['true', 'yes', '1', 'y', 't']

        # Validate tier input
        if tier:
            tier = tier.lower()
            if tier not in rarity_order:
                invalid_tier_embed = discord.Embed(title=f"Invalid tier specified.", description=f"Valid tiers are: {', '.join(rarity_order)}", color=discord.Color.red())
                await ctx.send(embed=invalid_tier_embed)
                return

        # Fetch owned items (list of item_id strings)
        owned_item_ids = await self.bank.get_inventory_strings(ctx.guild.id, user.id)

        # All items
        all_items = await self.bank.get_all_items()  # Returns a dict of item_id: Item

        # Prepare mapping
        tiered_items = {rarity: [] for rarity in rarity_order}

        for item_id, item in all_items.items():
            # Ensure 'rarity' attribute exists
            item_rarity = getattr(item, 'rarity', 'common').lower()  # Default to 'common' if not set

            if item_rarity not in tiered_items:
                continue  # Skip items with undefined rarity

            if tier and item_rarity != tier:
                continue  # Skip items not in the specified tier

            item_name = item.name
            is_owned = item_id in owned_item_ids

            if is_owned:
                if show_missing:
                    display_string = f"✅ {item.name}"
                else:
                    display_string = f"• {item.name}"
                tiered_items[item_rarity].append((item_name.lower(), display_string))
            elif show_missing:
                display_string = f"❌ ~~{item.name}~~"
                tiered_items[item_rarity].append((item_name.lower(), display_string))

        # Remove empty tiers
        tiered_items = {rarity: items for rarity, items in tiered_items.items() if items}

        # case no items owned
        if not tiered_items:
            description = "No items found."
            no_items_embed = discord.Embed(description=description, color=discord.Color.blue())
            no_items_embed.set_author(name=f"Inventory of {user.display_name}", icon_url=user.avatar.url if user.avatar else None)
            await ctx.send(embed=no_items_embed)
            return

        # Sort items within each tier alphabetically
        for rarity in tiered_items:
            tiered_items[rarity].sort(key=lambda x: x[0])

        # inventory embed
        embed = discord.Embed(color=discord.Color.blue())
        embed.set_author(name=f"Inventory of {user.display_name}", icon_url=user.avatar.url if user.avatar else None)

        for rarity in rarity_order:
            if rarity in tiered_items:
                # Extract display strings after sorting
                items_str = "\n".join([display_string for _, display_string in tiered_items[rarity]])
                # Format the field name based on whether a specific tier is selected
                rarity_name = f"{rarity_display_names[rarity]} Tier Collectables" if tier and rarity == tier else rarity_display_names[rarity]
                embed.add_field(name=rarity_name, value=items_str, inline=False)

        # Add footer based on invocation method and tier
        if ctx.interaction is not None:
            if tier:
                # Total items in the specified tier
                total_items_in_tier = len([item for item in all_items.values() if item.rarity.lower() == tier])
                # Owned items in the specified tier
                owned_items_in_tier = len([item_id for item_id in owned_item_ids if all_items.get(item_id) and all_items[item_id].rarity.lower() == tier])
                footer_text = f"{user.display_name} owns {owned_items_in_tier} out of {total_items_in_tier} collectable items in the {rarity_display_names[tier]} tier."
            else:
                # Total items overall
                total_items = len(all_items)
                # Owned items overall
                owned_items = len(owned_item_ids)
                footer_text = f"{user.display_name} owns {owned_items} out of {total_items} collectable items."
            embed.set_footer(text=footer_text)
        else:
            # Add footer if invoked via prefix command
            embed.set_footer(text="Please use /collectable inventory to show more information.")

        await ctx.send(embed=embed)

    

    @collectable.command(name="idlist", description="List of all collectable item IDs.")
    async def idlist(self, ctx):
        items = await self.bank.get_all_items()
        item_lines = [f"{item_id} : `{item.name}`" for item_id, item in items.items()]
        item_list = "\n".join(item_lines)
        # Create the embed
        embed = discord.Embed(title=f"All Collectable Item IDs", color=discord.Color.blue())
        embed.add_field(name=f"**Interpretation**", value=f"item id : item name", inline=False)
        embed.add_field(name=f"**IDs**", value=item_list, inline=False)
        embed.set_footer(text=f"There is a total of {len(items)} items to collect!")
        await ctx.send(embed=embed)



        
    async def cog_command_error(self, ctx, error: Exception):
        if isinstance(error, commands.CommandOnCooldown):
            pass
            #await util.send_cooldown_alert(ctx, error=error, deleteAfter=5)
        else:
            print(f"Unhandled error in guild {ctx.guild.id} for user {ctx.author.id}: {error}")

async def setup(client):
    await client.add_cog(Inventory(client))
