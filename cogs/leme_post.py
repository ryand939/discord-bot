from random import randrange
import caption_generator
from discord.ext import commands
from help import invoke_group_help
import util


# Leme is a made up word that usually describes a cute animal


class LemePost(commands.Cog, description="Leme pics and more"):


    def __init__(self, cli):
        self.cli = cli
        self.lemeList = ["https://api.thecatapi.com/v1/images/search", # lemeList[0] - CAT
                         "https://randomfox.ca/floof/",                 # lemeList[1] - FOX
                         "https://dog.ceo/api/breeds/image/random",# lemeList[2] - DOG
                         "https://random-d.uk/api/random"]
        self.captionGenerator = caption_generator.CaptionGenerator("./resources/fonts/impact.ttf")


    @commands.group(name='leme')
    async def leme(self, ctx):
        if ctx.invoked_subcommand is None:
            await invoke_group_help(ctx.cog.walk_commands(), ctx)


    @leme.command(name="new", description="Random leme.")
    async def new(self, ctx):
        randnum = randrange(len(self.lemeList))
        if randnum == 0: await self.cat(ctx)
        elif randnum == 1: await self.fox(ctx)
        elif randnum == 2: await self.dog(ctx)
        else: await self.duck(ctx)


    @leme.command(name="cat", description="Leme cat.")
    async def cat(self, ctx):
        data = await util.get_json_from_url(self.lemeList[0])
        await ctx.send(data[0]['url'])


    @leme.command(name="dog", description="Leme dog.")
    async def dog(self, ctx):
        data = await util.get_json_from_url(self.lemeList[2])
        await ctx.send(data['message'])


    @leme.command(name="duck", description="Leme duck.")
    async def duck(self, ctx):
        data = await util.get_json_from_url(self.lemeList[3])
        await ctx.send(data['url'])


    @leme.command(name="fox", description="Leme fox.")
    async def fox(self, ctx):
        data = await util.get_json_from_url(self.lemeList[1])
        await ctx.send(data['image'])





async def setup(client):
    await client.add_cog(LemePost(client))
