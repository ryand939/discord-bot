from random import randrange
import caption_generator
from discord.ext import commands
from help import CustomHelpCommand
import util


# Leme is a made up word that usually describes a cute animal


class LemePost(commands.Cog, description="Leme pics and more"):


    def __init__(self, cli):
        self.cli = cli
        self.lemeList = ["https://api.thecatapi.com/v1/images/search", # lemeList[0] - CAT
                         "https://randomfox.ca/floof/"]                # lemeList[1] - FOX


    @commands.group(name='leme')
    async def leme(self, ctx):
        if ctx.invoked_subcommand is None:
            # get the group and methods of this cog
            h = ctx.cog.walk_commands()
            helpObj = CustomHelpCommand()
            helpObj.context = ctx
            await helpObj.send_group_help(next(h))


    @leme.command(name="new", description="New randomly generated leme.")
    async def new(self, ctx):
        randnum = randrange(len(self.lemeList))
        if randnum == 0: await self.cat(ctx)
        else: await self.fox(ctx)



    @leme.command(name="cat", description="Lemes that look like cats.")
    async def cat(self, ctx):
        data = await util.get_json_from_url(self.lemeList[0])
        await ctx.send(data[0]['url'])


    @leme.command(name="fox", description="Lemes that look like foxes.")
    async def fox(self, ctx):
        data = await util.get_json_from_url(self.lemeList[1])
        await ctx.send(data['image'])


    @leme.command(name="this", description="This is leme.")
    async def this(self, ctx):
        img, ext = await util.get_last_img(ctx, 6) 
        if ext == -1: return 0
        cap_gen = caption_generator.CaptionGenerator("./impact.ttf")
        capImg = cap_gen.multiline_caption(img, "THIS IS LEME")
        await util.send_img(ctx, capImg, ext)



async def setup(client):
    await client.add_cog(LemePost(client))
