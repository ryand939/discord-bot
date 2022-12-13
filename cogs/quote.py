from random import shuffle
from help import invoke_group_help
import json
import os
from discord.ext import commands


class Quote(commands.Cog, name="Quote"):


    def __init__(self, client):
        self.client = client
        self.quoteDict = {}

        for filename in os.listdir("./resources/quotes"):
            if filename.endswith("_quotes.json"):
                quoteJSON = json.load(open(f"./resources/quotes/{filename}"))
                shuffle(quoteJSON)
                self.quoteDict.update({filename[:-12] : iter(quoteJSON)})
                self.quoteDict.update({filename[:-5] : quoteJSON})



    @commands.hybrid_group(name='quote')
    async def quote(self, ctx):
        if ctx.invoked_subcommand is None:
            await invoke_group_help(ctx.cog.walk_commands(), ctx)



    @quote.command(name="donut", description="DonutSandwich01 quote.")
    async def donut(self, ctx):
        await ctx.send(self.get_quote("donut", "DonutSandwich01"))

    

    # gets the next quote to send given a name key and the user's full alias
    def get_quote(self, nameKey, fullName):
        rtnStr = next(self.quoteDict[nameKey], None)
        if rtnStr is None:
            self.reset_quotes(nameKey)
            rtnStr = next(self.quoteDict[nameKey], None)
        rtnStr = f"\"{rtnStr}\"\n-{fullName}"
        return rtnStr


    # resets the quote iterator given a name
    def reset_quotes(self, name):
        quoteList = self.quoteDict[f'{name}_quotes']
        shuffle(quoteList)
        self.quoteDict[name] = iter(quoteList)


async def setup(client):
    await client.add_cog(Quote(client))
