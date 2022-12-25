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
                self.captionGenerator.multiline_caption(img, newInput[0].strip())
            else:
                self.captionGenerator.multiline_caption(img, newInput[0].strip(), newInput[1].strip())
            await ctx.send(file=await util.PIL_img_to_file(ctx, img, ext)) 


    @this.command(name="phone", description="Phone reaction.")
    async def phone(self, ctx):
        if ctx.interaction: await ctx.interaction.response.defer()
        # get the last sent png or jpg
        img, ext = await util.get_last_img(ctx, 6)
        # convert to cv2 img for editing
        cv2Img = numpy.asarray(img)
        # resize the img with the width of phone in template and maintain aspect ratio
        cv2Img = util.resize_img_cv2(cv2Img, width = 243)
        height, width, x = cv2Img.shape
        #crop image if too long
        if height > 430:
            height = 430
            cv2Img = cv2Img[0:height, 0:width]   
        # get destination cords for 4 corners of source image
        offsetx1, offsety1 = self.get_offset_cords((430/2) - (height/2), 37, 430)
        offsetx2, offsety2 = self.get_offset_cords((430/2) + (height/2), 37, 430)

        # where i want the source image to be
        destinationPoints = numpy.float32([[23 + offsetx1, 84 + offsety1],  # top left
                                      [265 + offsetx1, 64 + offsety1],      # top right
                                      [23 + offsetx2, 84 + offsety2],       # bottom left
                                      [265 +  offsetx2, 64 + offsety2]])    # bottom right

        sourcePoints = numpy.float32([[0, 0],            # top left
                                     [width, 0],         # top right
                                     [0, height],        # bottom left
                                     [width, height]])   # bottom right

        # map the 4 corners of the source image to the corresponding cords on the template
        matrix = cv2.getPerspectiveTransform(sourcePoints, destinationPoints)
        warpedImg = cv2.warpPerspective(cv2Img, matrix, self.phoneImage.size)
        # give the new image a background
        finalImg = cv2.cvtColor(warpedImg, cv2.COLOR_BGRA2BGR)
        # convert to a PIL image and paste the template overtop the source photo
        PILImg = Image.fromarray(finalImg)
        PILImg.paste(self.phoneImage, (0, 0), self.phoneImage)
        await ctx.send(file=await util.PIL_img_to_file(ctx, PILImg, ext)) 

    # gets the individual xy offsets for the corners of image to be placed on an angle
    def get_offset_cords(self, hypotenuse, oppositeSide, adjacentSide):
        angle = numpy.tan(oppositeSide/adjacentSide)
        offsetx = numpy.sin(angle)*hypotenuse
        offsety = numpy.cos(angle)*hypotenuse
        return offsetx, offsety


async def setup(client):
    await client.add_cog(ThisImage(client))