from random import shuffle
from help import CustomHelpCommand
import json
from discord.ext import commands


class DonutHypeman(commands.Cog, description="donut utilities", name="DonutHypeman"):


    def __init__(self, client):
        self.client = client
        file = open("./resources/quotes.json")
        # use iter and shuffle here to prevent rare dupe messages
        # also, I don't want messages to be predictable
        self.quotes = json.load(file)
        shuffle(self.quotes)
        self.quotesIter = iter(self.quotes)


    @commands.group(name='donut')
    async def donut(self, ctx):
        if ctx.invoked_subcommand is None:
            # get the group and methods of this cog
            h = ctx.cog.walk_commands()
            helpObj = CustomHelpCommand()
            helpObj.context = ctx
            await helpObj.send_group_help(next(h))


    @donut.command(name="quote", description="Random DonutSandwich01 quote.")
    async def quote(self, ctx):
        rtnStr = next(self.quotesIter, None)
        if rtnStr is None:
            shuffle(self.quotes)
            self.quotesIter = iter(self.quotes)
            rtnStr = next(self.quotesIter, None) 

        rtnStr = f"\"{rtnStr}\"\n-DonutSandwich01"
        await ctx.send(rtnStr)


    @commands.Cog.listener()
    async def on_message(self, message):
        auth = message.author
        if auth.id == 210544305163468800: #DonutSandwich01#0707 210544305163468800
            # all caps message or upload
            if message.content == message.content.upper():
                await message.add_reaction('🔥')


async def setup(client):
    await client.add_cog(DonutHypeman(client))
