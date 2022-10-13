from discord.ext import commands


class CustomHelpCommand(commands.HelpCommand):


    def __init__(self):
        super().__init__()


    async def send_bot_help(self, mapping):
        rtnStr = "daerbot commands\n"
        for cog in mapping:
            if cog is None:
                continue
            for command in cog.walk_commands():
                if len(command.parents) != 0:   # case subcommand
                    rtnStr += f"\t{command.name} : {command.description}\n"
                else:                           # case base/parent/groupname command
                    rtnStr += f"\n{self.context.bot.command_prefix}{command.name}\n"
        rtnStr = f"```{rtnStr}```"
        await self.get_destination().send(rtnStr)


    async def send_cog_help(self, cog):
        return await super().send_cog_help(cog)


    async def send_group_help(self, group):
        rtnStr = f"Usage: {self.context.bot.command_prefix}{group.name} {{subcommand}}\n\nSubcommands:\n"
        for cmd in group.commands:
            rtnStr += f"\t{cmd.name} : {cmd.description}\n"
        rtnStr = f"```{rtnStr}```"
        await self.get_destination().send(rtnStr)


    async def send_command_help(self, command):
        return await super().send_command_help(command)


