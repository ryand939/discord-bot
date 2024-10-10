# util.py

import json
from urllib.parse import urlparse
from io import BytesIO
from urllib.request import Request, urlopen
import discord
from PIL import Image
import requests
import cv2
from discord import Embed

from datetime import timedelta
import math

# this file contains various useful functions used by other features

prefix = ">"
bot_directory = "./discord-bot/"

# ok these are some good failure and success colors I like to use
# i wish i could do something like var colours = {red: 0x00e600, green: 0xe60000} 
# but i dont think this is possible in python
success_green = 0x00e600
failure_red = 0xe60000
default_blue = 0x03b6fc
warning_yellow = 0xfcd703

# creates a standardised embed message with timestamp
def get_embed(title, content=None, attachment=None, col=0x3897f0):
    embed = Embed(title=title, color=col)
    embed.description = content
    embed.set_image(url=attachment)
    embed.timestamp = discord.utils.utcnow()
    return embed

    


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


def appropriate_suffix(number: int):
    number = number % 10
    if number in [0, 4, 5, 6, 7, 8, 9]: return "th"
    elif number == 1: return "st"
    elif number == 2: return "nd"
    else: return "rd"




def get_command_text(ctx, with_all_params = False):
    if hasattr(ctx, 'prefix') and ctx.prefix: 
        command_prefix = ctx.prefix.strip()
    else: 
        command_prefix = "/"
    if ctx.command: 
        command_name = ctx.command.qualified_name
    else: 
        command_name = "unknown command"
    if with_all_params:
        text = f"{command_prefix}{command_name} " + " ".join([f"<{param.name}>" for param in ctx.command.params.values() if param.name != 'self' and param.kind in [param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD]])
    else: text = f"{command_prefix}{command_name}"
    return text



def get_user_args(ctx):
    message_words = ctx.message.content.split()
    command_full_name_with_prefix = ctx.prefix + ctx.command.qualified_name
    command_words = command_full_name_with_prefix.split()
    num_words_to_skip = len(command_words)
    user_args = message_words[num_words_to_skip:]
    return user_args



def get_command_and_args(ctx):
    user_args = get_user_args(ctx)
    command_part_name = get_command_text(ctx, with_all_params=False)
    input_command = f"{command_part_name} {' '.join(user_args)}"
    return input_command



async def send_error_embed(ctx, title, description, delete_after=10, footer=None, send=True, error=True, duration_minutes=None):
    embed = discord.Embed( description=description, color=failure_red, timestamp=discord.utils.utcnow())
    embed.set_author(name=f"Error: {title}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    
    if not error: 
        
        warning_end = discord.utils.utcnow() + timedelta(seconds=duration_minutes)
        timestamp_end = math.floor(warning_end.timestamp())
        string_timer = f"<t:{timestamp_end}:R>"
        embed.color = warning_yellow
        embed.set_author(name=f"Warning: {title}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        embed.add_field(name="Warning ends:", value=string_timer)
    if not footer:  embed.set_footer(text=f"{get_command_text(ctx, with_all_params=False)}")
    else:           embed.set_footer(text=footer)


    if send: await send_embed_delete_after(ctx=ctx, embed=embed, delete_after=delete_after)
    else: return embed
    
# for some reason, sending embeds with deleteafter or ephemeral is confusing af!
async def send_embed_delete_after(ctx, embed, delete_after=None):
    is_interaction = hasattr(ctx, 'interaction') and isinstance(ctx.interaction, discord.Interaction) and ctx.interaction is not None

    if is_interaction:
        interaction = ctx.interaction
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(embed=embed, ephemeral=(delete_after is not None))
            else:
                await interaction.followup.send(embed=embed, ephemeral=(delete_after is not None))
        except discord.InteractionResponded:
            await interaction.followup.send(embed=embed, ephemeral=(delete_after is not None))
    else:
        await ctx.send(embed=embed, delete_after=delete_after)