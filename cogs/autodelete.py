import os
import discord
from help import invoke_group_help
from discord.ext import commands, tasks
import util
from config import BotConfig


class Autodelete(commands.Cog, description="admin autodelete commands"):


    def __init__(self, client):
        self.client = client
        self.config = BotConfig("./resources/storage/autodelete.json")
        self.serverList = self.config.get_list()
        self.messageList = {}
        self.timerList = []



    @commands.hybrid_group(name='autodelete',hidden=True)
    async def autodelete(self, ctx):
        if ctx.invoked_subcommand is None:
            await invoke_group_help(ctx.cog.walk_commands(), ctx)


    # register / set channel for autodelete
    @autodelete.command(name="set", description="Register/set channel.", aliases=["register"],hidden=True)
    @commands.has_permissions(administrator=True)
    async def register(self, ctx, num):
        serverID = str(ctx.guild.id)
        channelID = str(ctx.channel.id)
        # turn off AD for this channel if input "off" or <=0
        if (not num.isdigit() and num == "off") or int(num) <= 0:
            await ctx.send(f"Autodelete: Disabled for channel ```{channelID}```")
            # remove setting from local config and update the server setting list
            self.config.clear(serverID, channelID)
            self.serverList = self.config.get_list()
            # remove from messageList
            self.messageList.pop(channelID, None)
            # cancel and remove timer
            timer = self.get_timer(channelID)
            self.timerList.remove(timer)
            timer[1].cancel()
            return
        # valid request, register channel with autodelete
        msg = await ctx.send(f"Autodelete: Catching up on deletes, please be patient. " + 
                    "For this operation to be successful, the oldest unpinned message in the channel must be no older than 14 days.")
        self.config.set(serverID, channelID, int(num))
        self.serverList = self.config.get_list()
        await self.catchup(ctx)
        rtnStr = f"Autodelete: Done. Deleting after the {num}{util.appropriate_suffix(int(num))} message."
        await msg.edit(content=rtnStr)


    # needed in cases where somehow an unpinned message doesnt get deleted
    # this could happen in the case of an old message being unpinned, or message sent while bot lost connection
    # this method validates tthat he channels in a guild have had old messages deleted
    @autodelete.command(name="catchup", description="Catch up on undeleted messages.", aliases=["cu"],hidden=True)
    @commands.has_permissions(administrator=True)
    async def catchup(self, ctx):
        await self.load_guild(ctx.guild)


    # takes a guild and prepares each channel registered with autodelete
    async def load_guild(self, guild, singleChannel=None):
        obligations = self.config.get_list(str(guild.id)) if singleChannel is None else [singleChannel]

        if obligations is not None:
            for index in range(0, len(obligations)):
                channel = self.client.get_channel(int(obligations[index][0]))
                print(f"[Autodelete] Loading messages in {channel.guild.name}: #{channel.name}")
                messages = [message async for message in channel.history(limit=None)]
                self.messageList.update({obligations[index][0]: await self.delete_messages(channel, messages, obligations[index][1], len(messages))})

    @commands.Cog.listener()
    async def on_message(self, message):
        # if there is no AD setting for this server, do nothing
        if not str(message.channel.id) in self.messageList.keys(): return
        # store the latest message at front of queue
        self.messageList[str(message.channel.id)].insert(0, message)
        # start a timer to accumulate messages before deleting, if timer already exists, do nothing
        # this makes sure i only send one delete request every 15s, no more getting rate limited
        if not self.get_timer(message.channel.id):
            # what index to stop deleting
            timer = tasks.loop(seconds=15, count=2)(self.delete_List)
            self.timerList.append([str(message.channel.id), timer])
            self.timerList[-1][1].start(message.channel, self.timerList[-1])


    # this function runs every 15s, twice
    # 15s passes, then the 2nd iteration removes the timer and deletes the accumulated messsages
    async def delete_List(self, channel, timer):
        if timer[1].current_loop == 1:
            stop = self.serverList[str(channel.guild.id)][str(channel.id)]
            self.timerList.remove(timer)
            deleteList = self.messageList[str(channel.id)][stop:]
            self.messageList[str(channel.id)] = self.messageList[str(channel.id)][:stop]
            await self.delete_messages(channel, deleteList, 0, len(deleteList))
            timer[1].cancel()

    # deletes messages until a pin is hit, or the max range for mass delete is hit, then calls itself. 
    # ends when stop index is hit
    async def delete_messages(self, channel, messages, stop, upperRange):
        if stop >= upperRange: 
                return messages[:upperRange]
        lowerRange = upperRange - 100 if upperRange - stop >= 100 else stop
        for index in range(upperRange, lowerRange - 1, -1):
            # base case
            if index == stop: 
                await channel.delete_messages(messages[stop:upperRange])
                return messages[:stop]
            # found a pin, update delete range to avoid deleting
            elif messages[index - 1].pinned: 
                await channel.delete_messages(messages[index:upperRange])
                return await self.delete_messages(channel, messages, stop, index - 1)
        await channel.delete_messages(messages[lowerRange:upperRange])
        return await self.delete_messages(channel, messages, stop, lowerRange)

    # gets the timer associated with a channel if one exists
    def get_timer(self, channelID):
        for timer in self.timerList:
            if timer[0] == str(channelID):
                return timer
        return None

    @catchup.error
    @register.error
    async def invalid_user(self, ctx, error):
        if ctx.interaction is None: await ctx.message.delete()
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("U need admin for that kid", delete_after=3)
        else:
            print(error)

# load the cog and prepare each guild registered with autodelete
async def setup(client):
    cogInstance = Autodelete(client)
    await client.add_cog(cogInstance)
    for guild in client.guilds:
        if str(guild.id) in cogInstance.serverList.keys():
            await cogInstance.load_guild(guild)


