# economy.py

import discord
from help import invoke_group_help
import util
from discord.ext import commands
from bank import Bank
from util import get_embed


class Economy(commands.Cog, description="participate in the daerconomy"):


    def __init__(self, client):
        self.client = client
        self.bank = Bank()
        # per user cooldown, used for rewarding activity
        self.messageEarnCooldown = commands.CooldownMapping.from_cooldown(1, 330, commands.BucketType.user)
        # passive reward for chatting
        self.chatReward = 10


    @commands.hybrid_group(name='econ')
    async def econ(self, ctx):
        if ctx.invoked_subcommand is None:
            await invoke_group_help(ctx.cog.walk_commands(), ctx)



    @econ.command(name="redeem", description="Redeem 100 daercoin.")
    @commands.cooldown(1, 60*60*6, commands.BucketType.member)
    async def redeem(self, ctx):
        await self.bank.deposit(ctx.guild.id, ctx.author.id, 100)
        balance = await self.bank.balance(ctx.guild.id, ctx.author.id)
        redeem_embed = get_embed(title=None, content=f"They now have a balance of `{balance}` daercoin", col=util.success_green)
        redeem_embed.set_author(name=f"{ctx.author.display_name} redeemed 100 daercoin", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        redeem_embed.set_footer(text=util.get_command_text(ctx))
        await ctx.send(embed=redeem_embed)
    

    @econ.command(name="balance", description="Your daercoin balance.", aliases=["bal"])
    async def balance(self, ctx, user: discord.Member = None):
        user = ctx.author if not user else user

        balance_embed = get_embed(title=None, content=f"{user.display_name} currently has a balance of `{await self.bank.balance(ctx.guild.id, user.id)}` daercoin.")
        balance_embed.set_author(name=f"{user.display_name}'s balance", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        balance_embed.set_footer(text=util.get_command_text(ctx))
        await ctx.send(embed=balance_embed)
    

    @econ.command(name="gift", description="Gift daercoin to user.")
    async def gift(self, ctx, user: discord.Member, amount: int):

        # some checks to make sure donation is allowed
        if amount <= 0 or user.bot or user == ctx.author:
            if ctx.interaction is None: await ctx.message.delete()
            await util.send_error_embed(ctx=ctx, title="Donation Failed", description="This donation is forbidden.", delete_after=10)

        # see if they have enough DC and withdraw and donate if so
        elif await self.bank.withdraw(ctx.guild.id, ctx.author.id, amount):
            # SUCCESS CASE
            await self.bank.deposit(ctx.guild.id, user.id, amount)
            gift_embed = discord.Embed(description=f"{amount} daercoin has been transferred to {user.display_name}'s balance.", 
                                       color=util.success_green, timestamp=discord.utils.utcnow())
            gift_embed.set_author(name=f"Successfully gifted daercoin to {user.display_name}", icon_url=user.display_avatar.url if user.display_avatar else None)
            gift_embed.set_footer(text=f"Daercoin gifted by {ctx.author}", icon_url=ctx.author.display_avatar.url if ctx.author.display_avatar else None)
            gift_embed.add_field(name="Donor", value=f"{ctx.author.mention}", inline=True)
            gift_embed.add_field(name="Recipient", value=f"{user.mention}", inline=True)
            gift_embed.add_field(name="Total Gifted", value=f"`{amount} daercoin`", inline=True)
            await ctx.send(embed=gift_embed)
        # FAIL they dont have enough DC
        else:
            if ctx.interaction is None: 
                await ctx.message.delete()
            await util.send_error_embed(ctx=ctx, title="Donation Failed", description=f"You can't afford to make a `{amount}` daercoin donation!", delete_after=10)


    @econ.command(name="top", description="Top 10 most richest users.")
    async def top(self, ctx):
        leaderboard = await self.bank.leaderboard(ctx.guild.id)
        max_range = min(len(leaderboard), 10) 

        if max_range == 0:
            no_leaderboard_embed = discord.Embed(
                title="Top 10 Richest Daercoin Holders",
                description="No users have daercoin yet.",
                color=discord.Color.blue()
            )
            await ctx.send(embed=no_leaderboard_embed)
            return

        # embed
        embed = discord.Embed(color=discord.Color.gold(), timestamp=discord.utils.utcnow())
        embed.set_author(name="Top 10 Richest Daercoin Holders", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        embed.set_footer(text=util.get_command_text(ctx))
        

        # leaderboard string
        leaderboard_str = ""
        for rank in range(max_range):
            user_id, balance = leaderboard[rank]
            member = ctx.guild.get_member(int(user_id))

            # members who have left the server
            if member is None:
                # remove the user from the leaderboard
                await self.bank.remove(ctx.guild.id, user_id)
                print(f"Removed user with ID {user_id} from the leaderboard as they have left the server.")
                continue  # Skip to the next user

            # only include users with a positive balance. dont know how they would get negative but still
            if balance <= 0:
                continue

            if rank == 0: rank_str = "🥇"
            elif rank == 1: rank_str = "🥈"
            elif rank == 2: rank_str = "🥉"
            else: rank_str = f"{rank + 1}th"

            # truncate the username if necessary
            display_name = member.display_name
            max_name_length = 20  # Adjust as needed
            if len(display_name) > max_name_length:
                display_name = display_name[:max_name_length - 3] + "..."

            # format the balance with comma separators
            formatted_balance = f"{balance:,} DC"

            # line for each leaderboard entry
            leaderboard_str += f"{rank_str}. **{display_name}** - `{formatted_balance}`\n" if rank_str[-1] == "h" else f"{rank_str}  **{display_name}** - `{formatted_balance}`\n"


        embed.description = leaderboard_str


        await ctx.send(embed=embed)





    # give user some daercoin if they talk, on cooldown
    # this cmd runs through on_message.py to ensure it executes before any subcommand in this cog
    # otherwise, the order is subcmd->activity_bonus. This makes for instantly outdated balance printing, for example.
    async def activity_bonus(self, message):
        if message.author.bot: return
        bucket = self.messageEarnCooldown.get_bucket(message)
        if not bucket.update_rate_limit(): 
            await self.bank.deposit(message.guild.id, message.author.id, self.chatReward)

    
    async def cog_command_error(self, ctx, error: Exception):
        if isinstance(error, commands.CommandOnCooldown):
            pass
        else:
            print(f"Unhandled error in guild {ctx.guild.id} for user {ctx.author.id}: {error}")

        

async def setup(client):
    await client.add_cog(Economy(client))
