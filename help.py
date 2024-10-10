# help.py

from discord.ext import commands
import discord


class CustomHelpCommand(commands.HelpCommand):

    def __init__(self):
        super().__init__()


    async def send_bot_help(self, mapping):
        embed = discord.Embed(
            title="Daerbot Commands",
            description="Enter a command to view its subcommands, or use slash commands to autofill.",
            color=discord.Color.blue()
        )

        for cog, commands_list in mapping.items():
            if cog is None:
                continue  # commands not belonging to any cog
            if not commands_list:
                continue  # skip cogs without commands

            # Get cog description
            cog_desc = cog.description or "No description."

            # loop through base commands (ignore subcommands)
            for command in commands_list:
                if len(command.parents) != 0:
                    continue  # subcommand

                cmd_name = f">{command.name}"

                
                embed.add_field(
                    name=f"**{cmd_name}**",
                    value=cog_desc,
                    inline=False
                )

        await self.get_destination().send(embed=embed)
    
    async def command_not_found(self, command):
        raise commands.CommandNotFound(command)
        
    
    async def send_cog_help(self, cog):
        return await super().send_cog_help(cog)

    async def send_group_help(self, group):
        embed = discord.Embed(
            title=f"\>{group.name} help",
            color=discord.Color.blue()
        )

        usage = f"{self.context.prefix}{group.name} <subcommand>"
        embed.add_field(
            name="**--Usage**",
            value=f"`{usage}`",
            inline=False
        )

        # subcommands
        if group.commands:
            subcommands = [
                f"**{cmd.name}** : `{cmd.description or 'No description.'}`"
                for cmd in group.commands
                if not cmd.hidden
            ]
            subcommands_str = "\n".join(subcommands) if subcommands else "No subcommands available."

            embed.add_field(
                name="**--Subcommands**",
                value=f"{subcommands_str}",
                inline=False
            )
        else:
            embed.add_field(
                name="Subcommands",
                value=f"`This command has no subcommands.`",
                inline=False
            )

        embed.set_footer(text="Use slash commands for a better experience and use >help for a list of all commands.")

        await self.get_destination().send(embed=embed)
    
    
    async def send_command_help(self, command):
        return await super().send_command_help(command)


async def invoke_group_help(cog, ctx):
    helpObj = CustomHelpCommand()
    helpObj.context = ctx
    await helpObj.send_group_help(next(cog))
