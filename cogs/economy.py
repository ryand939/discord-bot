import os
import discord
from help import invoke_group_help
import util
from discord.ext import commands
from bank import Bank


class Economy(commands.Cog, description="economy commands"):


    def __init__(self, client):
        self.client = client
        self.bank = Bank()
        # per user cooldown, used for rewarding activity
        self.messageEarnCooldown = commands.CooldownMapping.from_cooldown(1, 120, commands.BucketType.user)
        # reward for chatting
        self.chatReward = 2


    @commands.hybrid_group(name='econ')
    async def econ(self, ctx):
        if ctx.invoked_subcommand is None:
            await invoke_group_help(ctx.cog.walk_commands(), ctx)


    @econ.command(name="redeem", description="Redeem 100 daercoin.")
    @commands.cooldown(1, 60*60*6, commands.BucketType.member)
    async def redeem(self, ctx):
        self.bank.deposit(ctx.guild.id, ctx.author.id, 100)
        balance = self.bank.balance(ctx.guild.id, ctx.author.id)
        await ctx.send(f"Redeemed successfully. Your new daercoin balance is: ${balance}")


    @econ.command(name="balance", description="Your daercoin balance.", aliases=["bal"])
    async def balance(self, ctx, user: discord.Member = None):
        if not user: 
            # no user param, user is author
            await ctx.send(f"Your current daercoin balance is: ${self.bank.balance(ctx.guild.id, ctx.author.id)}")
        else: 
            await ctx.send(f"{user.display_name}'s current daercoin balance is: ${self.bank.balance(ctx.guild.id, user.id)}")

    
    @econ.command(name="gift", description="Gift daercoin to user.")
    async def gift(self, ctx, user: discord.Member, amount: int):
        if amount <= 0 or user.bot:
            if ctx.interaction is None: 
                await ctx.message.delete()
            await ctx.send(f"Invalid donation.", delete_after=3)
        elif self.bank.withdraw(ctx.guild.id, ctx.author.id, amount):
            self.bank.deposit(ctx.guild.id, user.id, amount)
            await ctx.send(f"Gifted {amount} daercoin successfully to {user.display_name}.")
        else:
            if ctx.interaction is None: 
                await ctx.message.delete()
            await ctx.send(f"You can't afford that!", delete_after=3)

    @econ.command(name="top", description="Top 10 most richest users.")
    async def top(self, ctx):
        leaderboard = self.bank.leaderboard(ctx.guild.id)
        maxRange = len(leaderboard) if len(leaderboard) < 10 else 10
        rtnStr = f"most richest daercoin holders:\n\n{'Name' : <16}{'$DC' : ^12}\n"
        for x in range(0, maxRange):
            member = ctx.guild.get_member(int(leaderboard[x][0]))
            # member left the server cannot be resolved
            if member is None:
                print(f"Removing unknown user: {leaderboard[x]}")
                self.bank.remove(ctx.guild.id, leaderboard[x][0])
                return await self.top(ctx)
            if leaderboard[x][1] > 0:
                rtnStr += f"{member.name: <16}{str(leaderboard[x][1]) : ^12}\n"
        rtnStr = f'```{rtnStr}```'
        await ctx.send(rtnStr)



    # give user some daercoin if they talk, on cooldown
    # this cmd runs through on_message.py to ensure it executes before any subcommand in this cog
    # otherwise, the order is subcmd->activity_bonus. This makes for instantly outdated balance printing, for example.
    async def activity_bonus(self, message):
        if message.author.bot: return
        bucket = self.messageEarnCooldown.get_bucket(message)
        if not bucket.update_rate_limit(): 
            self.bank.deposit(message.guild.id, message.author.id, self.chatReward)

    
    async def cog_command_error(self, ctx, error: Exception):
        if isinstance(error, commands.CommandOnCooldown):
            await util.send_cooldown_alert(ctx, error=error, deleteAfter=5)

        

async def setup(client):
    await client.add_cog(Economy(client))
