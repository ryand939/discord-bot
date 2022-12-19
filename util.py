import json
from urllib.parse import urlparse
from io import BytesIO
from urllib.request import Request, urlopen
import discord
from PIL import Image
import requests

# testing
import cv2
import numpy

# this file contains various useful functions used by other features


# gets the last png or jpeg not sent by bot within range. Return (-1, -1) if fail
async def get_last_img(ctx, range):
    async for message in ctx.channel.history(limit=range):
        # check if current message has attachment png/jpeg
        if message.embeds or len(message.attachments) > 0:
            # determine if message is a file upload or imglink
            # then check if the ext is png or jpg, else continue
            if len(message.attachments) > 0:
                attachmentfile = message.attachments[0]
                ext = urlparse(attachmentfile.url).path.split(".", 1)[1].upper()
            else:
                attachmentfile = message.content
                path = urlparse(attachmentfile).path.split(".")
                if len(path) <= 1:
                    continue
                ext = path[-1].upper()

            if ext != "PNG" and ext != "JPG":
                continue

            response = requests.get(attachmentfile)
            img = Image.open(BytesIO(response.content))
            ext = 'JPEG' if ext.lower() == 'jpg' else ext
            return img, ext
    return -1, -1


# converts pil image to discord sendable file
async def PIL_img_to_file(ctx, img, ext):
        bytes = BytesIO()
        img.save(bytes, format=ext)
        bytes.seek(0)
        return discord.File(fp=bytes, filename='image.png')


# get ID of last bot message in range
async def get_bot_message(ctx, range):
    async for message in ctx.channel.history(limit=range):
        if message.author == ctx.me:
            return message
    return None


# gets json data from a url
async def get_json_from_url(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urlopen(req) as url:
        return json.load(url)

# i have a dedicated channel for recieving images sent by this bot
# the bot sends the image, and returns the img url discord creates
async def get_url_for_image(ctx, file):

    # hardcoded guild name and channel
    guildName = "game zone"
    channelID = 1031022822031642626

    for guild in ctx.bot.guilds:
        if guild.name == guildName:
            msg = await guild.get_channel(channelID).send(file=file)
    return msg.attachments[0].url


# resizes an image and keeps the aspect ratio
def resize_img_cv2(img, width=None, height=None, inter = cv2.INTER_AREA):
    (h, w) = img.shape[:2]
    if width is None and height is None:
        return img
    if width is None:
        ratio = height / float(h)
        dimensions = (int(w * ratio), height)
    else:
        ratio = width / float(w)
        dimensions = (width, int(h * ratio))
    return cv2.resize(img, dimensions, interpolation = inter)

# takes a seconds integer and returns a dictionary with the hours/minutes/seconds
def parse_delay(seconds):
    if seconds < 60:
        return {"seconds":seconds}
    minutes = seconds // 60
    seconds = seconds % 60
    if minutes < 60: 
        return {"minutes":minutes, "seconds":seconds}
    hours = minutes // 60
    minutes = minutes % 60
    if hours < 24:
        return {"hours":hours, "minutes":minutes, "seconds":seconds}

async def send_cooldown_alert(ctx, error: Exception, deleteAfter = None):
    # if a slash command wasn't used, delete the original message
    if ctx.interaction is None: 
        await ctx.message.delete()
    # get a dictionary with delay in hours/minutes/seconds
    cooldown = parse_delay(int(error.retry_after))
    # create the cooldown string
    if "hours" in cooldown: cooldownTime = f"{cooldown['hours']} hours, {cooldown['minutes']} minutes, and {cooldown['seconds']} seconds"
    elif "minutes" in cooldown: cooldownTime = f"{cooldown['minutes']} minutes and {cooldown['seconds']} seconds"
    else: cooldownTime = f"{cooldown['seconds']} seconds"
    # send final message
    await ctx.send(f"{ctx.bot.command_prefix}{ctx.command} on cooldown. Try again in {cooldownTime}.", delete_after=deleteAfter)
        
