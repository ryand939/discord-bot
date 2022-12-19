from caption_generator import CaptionGenerator
from help import invoke_group_help
import discord
from discord.ext import commands
from PIL import Image
import util
import cv2
import numpy


class ThisImage(commands.Cog, description="preset image editor"):


    def __init__(self, client):
        self.client = client
        self.captionGenerator = CaptionGenerator("./resources/fonts/impact.ttf")
        self.phoneImage = Image.open("./resources/this_image/phone.png")


    @commands.hybrid_group(name='this')
    async def this(self, ctx):
        if ctx.invoked_subcommand is None:
            await invoke_group_help(ctx.cog.walk_commands(), ctx)


    @this.command(name="leme", description="This is leme.")
    async def leme(self, ctx):
        await ctx.interaction.response.defer()
        img, ext = await util.get_last_img(ctx, 6) 
        if ext == -1: return 0
        RGBImg = img.convert('RGB')
        capImg = self.captionGenerator.multiline_caption(RGBImg, "THIS IS LEME")
        await ctx.send(file=await util.PIL_img_to_file(ctx, capImg, ext)) 

    @this.command(name="caption", description="Custom image caption.")
    async def new(self, ctx, *, input=None):
        if input is not None:
            if ctx.interaction: await ctx.interaction.response.defer()
            newInput = input.split(":", 1)                  # get top text and bottom text from input=toptext:bottomtext
            img, ext = await util.get_last_img(ctx, 6)      # get the last image sent in chat and its file ext
            if ext == -1: return 0                          
            if len(newInput) == 1:
                capImg = self.captionGenerator.multiline_caption(img, newInput[0].strip())
            else:
                capImg = self.captionGenerator.multiline_caption(img, newInput[0].strip(), newInput[1].strip())
            await ctx.send(file=await util.PIL_img_to_file(ctx, img, ext)) 


    @this.command(name="phone", description="Phone reaction.")
    async def phone(self, ctx):
        if ctx.interaction: await ctx.interaction.response.defer()
        img, ext = await util.get_last_img(ctx, 6)
        cv2_img = numpy.asarray(img)
        cv2_img = util.resize_img_cv2(cv2_img, width = 243)
        height, width, x = cv2_img.shape
        #crop image if too long
        if height > 430:
            height = 430
            cv2_img = cv2_img[0:height, 0:width]    
        
        offsetx1, offsety1 = self.get_offset_cords((430/2) - (height/2), 37, 430)
        offsetx2, offsety2 = self.get_offset_cords((430/2) + (height/2), 37, 430)

        transform_pt = numpy.float32([[23 + offsetx1, 84 + offsety1],     # top left
                                      [265 + offsetx1, 64 + offsety1],    # top right
                                      [23 + offsetx2, 84 + offsety2],     # bottom left
                                      [265 +  offsetx2, 64 + offsety2]])  # bottom right

        original_pt = numpy.float32([[0, 0],             # top left
                                     [width, 0],         # top right
                                     [0, height],        # bottom left
                                     [width, height]])   # bottom right

        matrix = cv2.getPerspectiveTransform(original_pt, transform_pt)
        warpedImg = cv2.warpPerspective(cv2_img, matrix, self.phoneImage.size)
        finalImg = cv2.cvtColor(warpedImg, cv2.COLOR_BGRA2BGR)
        PILImg = Image.fromarray(finalImg)
        PILImg.paste(self.phoneImage, (0, 0), self.phoneImage)
        await ctx.send(file=await util.PIL_img_to_file(ctx, PILImg, ext)) 


    def get_offset_cords(self, hypotenuse, oppositeSide, adjacentSide):
        angle = numpy.tan(oppositeSide/adjacentSide)
        offsetx = numpy.sin(angle)*hypotenuse
        offsety = numpy.cos(angle)*hypotenuse
        return offsetx, offsety


async def setup(client):
    await client.add_cog(ThisImage(client))