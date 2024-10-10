
import discord
from discord.ext import commands
from collections import deque
from datetime import timedelta
import math
import util

class AntiSpam(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.user_commands = {}
        self.warned_users = {}
        self.warning_limit = 5             # number of allowed commands before warning
        self.timeout_limit = 3             # number of allowed commands AFTER WARNING
        self.time_frame = 5                # time window in seconds to track user commands
        self.warning_duration = 600        # length of warning after receiving (seconds)
        self.timeout_duration = 5          # timeout duration (minutes)

    async def register_command_usage(self, user_id, ctx=None, is_error=False):
        current_time = discord.utils.utcnow()

        # init deque for new users
        if user_id not in self.user_commands:
            self.user_commands[user_id] = deque()

        # append timestamp for current cmd
        self.user_commands[user_id].append(current_time)

        # remove old timestamps outside of window
        while self.user_commands[user_id] and (current_time - self.user_commands[user_id][0]).total_seconds() > self.time_frame:
            self.user_commands[user_id].popleft()

        # check if the user has a warning, then check if it is expired ... if so remove
        if user_id in self.warned_users:
            warning_expires_at = self.warned_users[user_id]
            if current_time >= warning_expires_at:
                del self.warned_users[user_id]
                print(f"Spam warning expired for ID {user_id}.")

        # case user is not yet warned 
        if user_id not in self.warned_users:
            # if they have sent enough messages in the time window to receive a warning
            if len(self.user_commands[user_id]) >= self.warning_limit:
                # CASE USER IS SPAMMING!!! WARN THEM!!!
                if ctx: await self.send_warning(ctx)
                # add them to the warned user list with the expiry time
                self.warned_users[user_id] = current_time + timedelta(seconds=self.warning_duration)
                # reset their command list because now there is new criteria to get timed out
                self.user_commands[user_id].clear()
                print(f"Warned ID {user_id}.")

        # case they have already been warned
        else:
            # if they are exceeding their warned command limit which qualifies for timeout
            if len(self.user_commands[user_id]) >= self.timeout_limit:
                if ctx: await self.timeout_user(ctx)
                # reset now and we will start over when they are back!
                self.user_commands.pop(user_id, None)
                self.warned_users.pop(user_id, None)

    async def send_warning(self, ctx):
        try:
            await util.send_error_embed(
                ctx=ctx, title="Stop spamming!",
                description=(
                    f"**Please stop spamming daerbot commands.** Daerbot has received `{self.warning_limit}` or more commands from you "
                    f"in the past `{self.time_frame} seconds`. Please make an effort to slow down dramatically or "
                    f"you will receive a `{self.timeout_duration} minute` timeout on your next warning."
                ), delete_after=None, footer=None, send=True, error=False, duration_minutes=self.warning_duration)
        except discord.HTTPException as e:
            print(f"Failed to warn ID {ctx.author.id}: {e}")

    async def timeout_user(self, ctx):
        try:
            # Check if the bot has the 'moderate_members' permission
            if ctx.guild.me.guild_permissions.moderate_members:
                await ctx.author.timeout(timedelta(minutes=self.timeout_duration), reason="Spamming commands.")
                embed = discord.Embed( description="Why did you make me do that? Why spam daerbot commands? Please take some time to reflect.", color=util.failure_red, timestamp=discord.utils.utcnow())
                embed.set_author(name=f"{ctx.author.display_name} has been timed out for {self.timeout_duration} minutes.", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
                await ctx.send(embed=embed)
                print(f"ID {ctx.author.id} has been timed out for spamming commands.")
            else:
                await util.send_error_embed(
                    ctx=ctx, title="Unable to timeout user",
                    description=(f"{ctx.author.display_name} is spamming daerbot commands but daerbot does not have permission to timeout them as punishment..."),
                    delete_after=10, footer="daerbot antispam", send=True, error=True)
                print(f"Missing 'Moderate Members' permission to timeout ID {ctx.author.id}.")
        except discord.Forbidden:
            await util.send_error_embed(
                ctx=ctx, title="Unable to timeout user",
                description=(f"{ctx.author.display_name} is spamming daerbot commands but daerbot does not have permission to timeout them as punishment..."), 
                delete_after=10, footer="daerbot antispam", send=True, error=True)
            print(f"Failed to timeout ID {ctx.author.id}: Missing permissions.")
        except discord.HTTPException as e:
            await util.send_error_embed(
                ctx=ctx,
                title="Failed to Timeout User",
                description=f"Failed to timeout {ctx.author.display_name}: {e}",
                delete_after=10,
                footer="daerbot antispam",
                send=True,
                error=True
            )
            print(f"HTTPException while muting ID {ctx.author.id}: {e}")

    @commands.Cog.listener()
    async def on_command(self, ctx):
        user_id = ctx.author.id
        await self.register_command_usage(user_id, ctx=ctx, is_error=False)

    # ensure if someone leaves they are cleared out of memory
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        user_id = member.id
        self.user_commands.pop(user_id, None)
        self.warned_users.pop(user_id, None)

async def setup(bot):
    await bot.add_cog(AntiSpam(bot))