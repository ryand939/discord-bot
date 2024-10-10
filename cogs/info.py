from discord.ext import commands
import discord
import platform
import psutil
import datetime
from help import invoke_group_help
import util

def bytes_to_mb(bytes_amount):
    mb = bytes_amount / (1024 ** 2)
    return f"{int(mb)} MB"

class Info(commands.Cog, description="General information gathering commands"):

    def __init__(self, client):
        self.client = client
        self.start_time = datetime.datetime.now()

    @commands.hybrid_group(name='info')
    async def info(self, ctx):
        if ctx.invoked_subcommand is None:
            await invoke_group_help(ctx.cog.walk_commands(), ctx)

    @info.command(name='daerbot', description="All information about daerbot")
    async def daerbot(self, ctx):
        # get system information
        uname = platform.uname()
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        total_ram_bytes = memory.total
        total_ram_mb = bytes_to_mb(total_ram_bytes)

        uptime_delta = datetime.datetime.now() - self.start_time
        days = uptime_delta.days
        uptime_str = f"{days} day{'s' if days != 1 else ''}"

        python_version = platform.python_version()
        discord_version = discord.__version__
        total_guilds = len(self.client.guilds)
        total_users = sum(guild.member_count for guild in self.client.guilds)
        
        # embed
        embed = discord.Embed(title="Daerbot Information",color=discord.Color.blue(), timestamp=discord.utils.utcnow())
        embed.set_thumbnail(url=self.client.user.avatar.url if self.client.user.avatar else None)
        embed.add_field(name="", value=f"A discord.py bot running off a Raspberry Pi 4 in daer's living room!", inline=False)
        embed.add_field(name="**System**", value=f"{uname.system} {uname.release} {uname.version}", inline=True)
        embed.add_field(name="**Machine**", value=f"{uname.machine}", inline=True)
        embed.add_field(name="**Processor**", value=f"{uname.processor}", inline=True)
        embed.add_field(name="**CPU Usage**", value=f"{cpu_usage}%", inline=True)
        embed.add_field(name="**Memory Usage**", value=f"{memory.percent}% of {total_ram_mb}", inline=True)
        embed.add_field(name="**Disk Usage**", value=f"{disk.percent}%", inline=True)
        embed.add_field(name="**Python Version**", value=f"{python_version}", inline=True)
        embed.add_field(name="**discord.py Version**", value=f"{discord_version}", inline=True)
        embed.add_field(name="**Uptime**", value=f"{uptime_str}", inline=True)
        embed.add_field(name="**Servers**", value=f"{total_guilds}", inline=True)
        embed.add_field(name="**Users**", value=f"{total_users}", inline=True)
        embed.add_field(name="**Command Prefix**", value=f"{self.client.command_prefix}", inline=True)
        embed.set_footer(text="Use >help to list all commands.")
        
        await ctx.send(embed=embed)

    @info.command(name='uptime', description="More detailed daerbot uptime")
    async def uptime(self, ctx):
        # uptime
        uptime_since= int(self.start_time.timestamp())

        # embed with no title
        embed = discord.Embed(color=discord.Color.blue(), timestamp=discord.utils.utcnow())
        embed.set_author(name="Daerbot Uptime", icon_url=self.client.user.avatar.url if self.client.user.avatar else None)
        embed.set_footer(text=f"{util.get_command_text(ctx)}")
        # timestamp
        embed.description = f"As of right now, daerbot has seen ZERO DOWNTIME since <t:{uptime_since}:f> (<t:{uptime_since}:R>)!"

        await ctx.send(embed=embed)
        

    @info.command(name='whois', description="Get information about a Discord user. Defaults to self.")
    async def whois(self, ctx, user: discord.Member = None):
        # default to the command invoker
        user = user or ctx.author

        # Fetch the user for banner
        fetched_user = await self.client.fetch_user(user.id)

        # embed with the user top role color or default to blue
        color = user.color if user.color.value else discord.Color.blue()

        embed = discord.Embed(color=color, description=f"{user.mention}", timestamp=discord.utils.utcnow())

        # thumbnail is the user's avatar
        embed.set_thumbnail(url=user.display_avatar.url)
        if fetched_user.banner:
            embed.description += f"\n[Full Size Banner]({fetched_user.banner.url})"
            smaller_banner_url = f"{fetched_user.banner.url}?size=128"  # Adjust size as needed
            embed.set_image(url=smaller_banner_url)


        profile_url = f"https://discord.com/users/{user.id}"

        # Set the author field with the user's name linked to their profile and their avatar
        embed.set_author(
            name=f"{str(user)}🔗",
            icon_url=user.display_avatar.url,
            url=profile_url
        )
        # Online status and platform
        status = str(user.status).title() 
        platform_statuses = []
        if user.desktop_status != discord.Status.offline:
            platform_statuses.append(f"Status: `{status} (desktop)`")
        if user.mobile_status != discord.Status.offline:
            platform_statuses.append(f"Status: `{status} (mobile)`")
        if user.web_status != discord.Status.offline:
            platform_statuses.append(f"Status: `{status} (web)`")

        if platform_statuses:
            status_details = "\n".join(platform_statuses)
        else:
            status_details = ""

        # "User Info" field
        is_bot = "Yes" if user.bot else "No"
        creation_date = user.created_at
        user_info = (
            f"ID: `{user.id}`\n"
            f"Bot Account: `{is_bot}`\n"
            f"Account Created: <t:{int(creation_date.timestamp())}:R> - <t:{int(creation_date.timestamp())}:D>\n"
            f"{status_details}"
        )
        embed.add_field(name="User Info", value=user_info, inline=False)

        # "Guild Specific Info"
        guild = ctx.guild
        if guild:
            nickname = f"Nickname: `{user.nick}`\n" if user.nick else ""
            join_date = user.joined_at
            if join_date:
                join_date_str = f"<t:{int(join_date.timestamp())}:R> - <t:{int(join_date.timestamp())}:D>"
            else:
                join_date_str = "`Unknown`"

            # calc join position
            if join_date:
                # filter out members without a join date
                members = [m for m in guild.members if m.joined_at]
                # sort members by their join date
                members.sort(key=lambda m: m.joined_at)
                try:
                    join_position = [m.id for m in members].index(user.id) + 1  # pos start at 1
                    join_position_str = f"`{join_position} / {len(members)}`"
                except ValueError:
                    join_position_str = "`Unknown`"
            else:
                join_position_str = "`Unknown`"

            # Acknowledgements
            special_info = []
            if user == guild.owner:
                special_info.append("`Owner`")
            if user.guild_permissions.administrator:
                special_info.append("`Admin`")
            if user.guild_permissions.manage_guild and "`Admin`" not in special_info:
                special_info.append("`Manager`")
            if not special_info:
                special_info.append("`None`")

            if special_info[0] == "`None`":
                special_info_str = ""
            else:
                special_info_str = ", ".join(special_info)
                special_info_str = f"Acknowledgements: {special_info_str}\n"

            # roles (excluding @everyone)
            roles = [role for role in user.roles if role.name != "@everyone"]
            roles_sorted = sorted(roles, key=lambda r: r.position, reverse=True)
            roles_mentions = [role.mention for role in roles_sorted]
            roles_mentions.append("`@everyone`")
            roles_string = ", ".join(roles_mentions)
            # discord's embed field limit is 1024 characters
            if len(roles_string) > 1024:
                roles_string = roles_string[:1021] + "..."

            guild_info = (
                f"{nickname}"
                f"Joined Server: {join_date_str}\n"
                f"Join Position: {join_position_str}\n"
                f"{special_info_str}"
                f"Roles ({len(user.roles)}): {roles_string}"
            )
            embed.add_field(name=f"{guild.name.capitalize()} Specific Info", value=guild_info, inline=False)
        else:
            # not in guild context
            embed.add_field(name="Guild Specific Info", value="`Not in a guild context.`", inline=False)

        # Current activities
        activities = user.activities  # list of Activity objects
        if activities:
            activity_types = {}
            for activity in activities:
                # Get activity type
                if isinstance(activity, discord.CustomActivity):
                    activity_type = "Custom Status"
                    activity_name = f"`{activity.name}`" if activity.name else "`None`"
                elif isinstance(activity, discord.Spotify):
                    activity_type = "Listening to Spotify"
                    artists = ", ".join(activity.artists)
                    activity_name = f"`{activity.title}` by {artists}"
                elif isinstance(activity, discord.Game):
                    activity_type = "Playing"
                    if activity.details:
                        activity_name = f"`{activity.name} - {activity.details}`"
                    else:
                        activity_name = f"`{activity.name}`"
                elif isinstance(activity, discord.Streaming):
                    activity_type = "Streaming"
                    activity_name = f"`{activity.name}` on `{activity.platform}`"
                elif isinstance(activity, discord.Activity):
                    activity_type = activity.type.name.title()
                    if activity.details:
                        activity_name = f"`{activity.name} - {activity.details}`"
                    else:
                        activity_name = f"`{activity.name}`" if activity.name else "`None`"
                else:
                    activity_type = "`Unknown`"
                    activity_name = f"`{str(activity)}`"

                # Group by type
                if activity_type not in activity_types:
                    activity_types[activity_type] = []
                activity_types[activity_type].append(activity_name)

            # activity field content
            activity_field_lines = []
            for activity_type, names in activity_types.items():
                if len(names) > 1:
                    # case multiple activities of the same type
                    activity_line = f"{activity_type} ({len(names)}): {', '.join(names)}"
                else:
                    activity_line = f"{activity_type}: {names[0]}"
                activity_field_lines.append(activity_line)

            # total number of activities if more than one
            activity_field_name = f"Current Activities ({len(activities)})" if len(activities) > 1 else "Current Activity"

            embed.add_field(
                name=activity_field_name,
                value="\n".join(activity_field_lines),
                inline=False
            )


        embed.set_footer(
            text=f"Requested by {ctx.author}",
            icon_url=ctx.author.display_avatar.url
        )
        
        await ctx.send(embed=embed)


async def setup(client):
    await client.add_cog(Info(client))