import caption_generator
from help import CustomHelpCommand
from discord.ext import commands
import util


class Caption(commands.Cog, description="caption commands"):


    def __init__(self, cli):
        self.cli = cli
        self.captionGenerator = caption_generator.CaptionGenerator("./resources/fonts/impact.ttf")


    @commands.group(name='caption')
    async def caption(self, ctx):
        if ctx.invoked_subcommand is None:
            # get the group and methods of this cog
            groupObj = ctx.cog.walk_commands()
            helpObj = CustomHelpCommand()
            helpObj.context = ctx
            await helpObj.send_group_help(next(groupObj))


    @caption.command(name="new", description="Custom image caption.")
    async def new(self, ctx, *, input=None):
        if input is not None:
            newInput = input.split(":", 1)                  # get top text and bottom text from input=toptext:bottomtext
            img, ext = await util.get_last_img(ctx, 6)      # get the last image sent in chat and its file ext
            if ext == -1: return 0                          
            if len(newInput) == 1:
                capImg = self.captionGenerator.multiline_caption(img, newInput[0].strip())
            else:
                capImg = self.captionGenerator.multiline_caption(img, newInput[0].strip(), newInput[1].strip())
            await ctx.channel.send(file=await util.PIL_img_to_file(ctx, img, ext)) 


async def setup(client):
    await client.add_cog(Caption(client))