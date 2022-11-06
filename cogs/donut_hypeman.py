from random import shuffle
from help import invoke_group_help
import json
from discord.ext import commands


class DonutHypeman(commands.Cog, description="donut utilities", name="DonutHypeman"):


    def __init__(self, client):
        self.client = client
        file = open("./resources/quotes.json")
        # use iter and shuffle here to prevent rare dupe messages
        # also I don't want messages to be predictable
        self.quotes = json.load(file)
        shuffle(self.quotes)
        self.quotesIter = iter(self.quotes)


    @commands.group(name='donut')
    async def donut(self, ctx):
        if ctx.invoked_subcommand is None:
            await invoke_group_help(ctx.cog.walk_commands(), ctx)


    @donut.command(name="quote", description="DonutSandwich01 quote.")
    async def quote(self, ctx):
        rtnStr = next(self.quotesIter, None)
        if rtnStr is None:
            shuffle(self.quotes)
            self.quotesIter = iter(self.quotes)
            rtnStr = next(self.quotesIter, None) 

        rtnStr = f"\"{rtnStr}\"\n-DonutSandwich01"
        await ctx.send(rtnStr)


async def setup(client):
    await client.add_cog(DonutHypeman(client))
