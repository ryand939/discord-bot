
import discord
from discord.ext import commands
import util  # Ensure this is correctly imported based on your project structure
import inspect

from discord import Embed

from datetime import timedelta
import math


class ErrorHandler(commands.Cog):
    """
    A Cog for handling errors across all commands in the bot.
    """

    def __init__(self, bot):
        self.bot = bot

        # different delete after delays
        self.missing_argument_delete_after = 20
        self.bad_argument_delete_after = 20
        self.on_cooldown_delete_after = 15
        self.cmd_not_found_delete_after = 20

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        
        # prevent the handler from processing errors already handled by command error handlers
        if hasattr(ctx.command, 'on_error'):
            return

        if isinstance(error, commands.CommandNotFound):
            await self.handle_command_not_found(ctx, error)
            return

        # Handle specific error types
        if isinstance(error, commands.MissingRequiredArgument):
            await self.handle_missing_argument(ctx, error)
        elif isinstance(error, commands.BadArgument):
            await self.handle_bad_argument(ctx, error)
        elif isinstance(error, commands.CommandOnCooldown):
            await self.handle_cooldown(ctx, error)
        elif isinstance(error, commands.CheckFailure):
            
            pass
        else:
            # unexpected errors?
            print(f"Unhandled error: {error}")
            await util.send_error_embed(ctx, "What just happened?", "An unexpected error occurred. Specific details have been sent in console for daer.", delete_after=10)



    async def handle_command_not_found(self, ctx, error):
        title = "Command not found"
        description = f"There is no command `>{ctx.invoked_with}` recognized by daerbot. \n\nPlease ensure you are using subcommands with their respective group command prefix (i.e. `coinflip` can only be called via `>gamble coinflip`, **not** `>coinflip`, as it is a subcommand under `>gamble`)."

        await util.send_error_embed(ctx, title, description, delete_after=self.cmd_not_found_delete_after, footer="Type >help to list all daerbot commands")



    async def handle_missing_argument(self, ctx, error):
        missing_param = error.param.name if hasattr(error, 'param') else 'unknown'

        # attempt to get the type annotation of the missing parameter
        if hasattr(error.param, 'annotation'):
            param_annotation = error.param.annotation
            if param_annotation != inspect.Parameter.empty:
                # if the annotation is a type, get its name
                if isinstance(param_annotation, type):
                    param_type = " of type `" + param_annotation.__name__ + "`"
                else:
                    # for converters or other annotations, convert to string
                    param_type = " of type `" + str(param_annotation) + "`"
            else:
                param_type = ''
        else:
            param_type = ''

        title = "Missing required argument"
        description = f"You missed a required argument `{missing_param}`{param_type} for this command."

        embed = await util.send_error_embed(ctx, title, description, delete_after=self.missing_argument_delete_after, footer="Use slash commands for a better experience", send=False)

        # get input command that user entered
        input_command = util.get_command_and_args(ctx)

        embed.add_field(name="Usage", value=f"`{util.get_command_text(ctx, with_all_params=True)}`", inline=False)
        embed.add_field(name="Your input", value=f"`{input_command}`", inline=False)

        await util.send_embed_delete_after(ctx=ctx, embed=embed, delete_after=self.missing_argument_delete_after)



    async def handle_bad_argument(self, ctx, error):
        command_full_name = util.get_command_text(ctx, with_all_params=True)

        param_name = 'unknown'
        param_type = 'unknown'
        bad_value = 'unknown'

        # command signature
        signature = inspect.signature(ctx.command.callback)
        parameters = signature.parameters

        # remove 'self' and 'ctx'
        param_list = [param for param in parameters.values() if param.name not in ('self', 'ctx')]

        user_args = util.get_user_args(ctx)

        # identify which argument caused the error
        for i, param in enumerate(param_list):
            if i >= len(user_args):
                continue 
            arg = user_args[i]
            expected_type = param.annotation
            if expected_type == inspect.Parameter.empty:
                continue 
            try:
                converter = expected_type
                if isinstance(converter, type):
                    converter(arg)
                else:
                    await converter().convert(ctx, arg)
            except Exception:
                # conversion failed... so we found the problematic parameter
                param_name = param.name
                param_type = expected_type.__name__ if isinstance(expected_type, type) else str(expected_type)
                bad_value = arg
                bad_value_type = type(bad_value).__name__
                break

        # building embed
        title = "Invalid Argument"
        description = f"The argument `<{param_name}>` of type `{param_type}` received `\"{bad_value}\"` of type `{bad_value_type}` which is invalid for the given command."
        embed = await util.send_error_embed(ctx, title, description, delete_after=self.bad_argument_delete_after, footer="Use slash commands for a better experience", send=False)
        input_command = util.get_command_and_args(ctx)
        embed.add_field(name="Usage", value=f"`{command_full_name}`", inline=False)
        embed.add_field(name="Your input", value=f"`{input_command}`", inline=False)

        # and send
        await util.send_embed_delete_after(ctx=ctx, embed=embed, delete_after=self.bad_argument_delete_after)


    async def handle_cooldown(self, ctx, error):
        footer = ""
        if not hasattr(ctx, 'interaction') and ctx.interaction is not None and hasattr(ctx, 'message'):
            footer = "Try again when this message is deleted!"
            try: await ctx.message.delete()
            except discord.Forbidden: pass  # bot doesnt have delete permission
            except discord.NotFound: pass  # message already deleted. Sometimes i have two instances of daerbot running while i test it. one on pi, one on main pc
        
        # calc when the cooldown ends
        retry_after = int(math.ceil(error.retry_after))
        cooldown_end = discord.utils.utcnow() + timedelta(seconds=retry_after)
        cooldown_end_unix = math.floor(cooldown_end.timestamp())
        
        # timestamp formatting
        relative_time = f"<t:{cooldown_end_unix}:R>"
        full_time = f"<t:{cooldown_end_unix}:f>"
        
        cooldown_embed = Embed(description=f"`{util.get_command_text(ctx)}` is on cooldown. Try again {relative_time} on {full_time}",
            color=util.failure_red, timestamp=discord.utils.utcnow())
        
        cooldown_title = "used a command on cooldown"
        
        # embed author the user's name and avatar
        cooldown_embed.set_author(
            name=f"{ctx.author.display_name} {cooldown_title}" if hasattr(ctx, 'author') else f"Unknown User {cooldown_title}",
            icon_url=ctx.author.avatar.url if hasattr(ctx, 'author') and ctx.author.avatar else None)

        # default delete after 15 sec unless remaining cooldown is less than 15
        delete_after = self.on_cooldown_delete_after 
        if retry_after < delete_after:
            delete_after = retry_after

        if delete_after == retry_after: cooldown_embed.set_footer(text=footer)

        # determine if slash or reg cmd and send the thing
        await util.send_embed_delete_after(ctx=ctx, embed=cooldown_embed, delete_after=delete_after)




async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))