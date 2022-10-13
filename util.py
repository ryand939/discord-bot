import json
from urllib.parse import urlparse
from io import BytesIO
from urllib.request import Request, urlopen
import discord
from PIL import Image
import requests

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
                path = urlparse(attachmentfile).path.split(".", 1)
                if len(path) <= 1:
                    continue
                ext = path[1].upper()

            if ext != "PNG" and ext != "JPG":
                continue

            response = requests.get(attachmentfile)
            img = Image.open(BytesIO(response.content))
            ext = 'JPEG' if ext.lower() == 'jpg' else ext
            return img, ext
    return -1, -1


# sends a Pillow Image obj in discord chat
async def send_img(ctx, img, ext):
        bytes = BytesIO()
        img.save(bytes, format=ext)
        bytes.seek(0)
        file = discord.File(fp=bytes, filename='image.png')
        await ctx.channel.send(file=file)


# gets json data from a url
async def get_json_from_url(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urlopen(req) as url:
        return json.load(url)

