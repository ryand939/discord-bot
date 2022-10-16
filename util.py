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


# sends a Pillow Image obj in discord chat
async def send_PIL_img(ctx, img, ext):
        return await ctx.channel.send(file=await PIL_img_to_file(ctx, img, ext))


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
    for guild in ctx.bot.guilds:
        if guild.name == "game zone":
            msg = await guild.get_channel(1031022822031642626).send(file=file)
    return msg.attachments[0].url


# resizes an image and keeps the aspect ratio
def resize_img_cv2(img, width=None, height=None, inter = cv2.INTER_AREA):
    dim = None
    (h, w) = img.shape[:2]
    if width is None and height is None:
        return img
    if width is None:
        ratio = height / float(h)
        dimensions = (int(w * ratio), height)
    else:
        ratio = width / float(w)
        dimensions = (width, int(h * ratio))
    return  cv2.resize(img, dimensions, interpolation = inter)


