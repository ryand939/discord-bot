import caption_generator
from help import CustomHelpCommand
from discord.ext import commands
from PIL import Image
import util
import cv2
import numpy


class ThisImage(commands.Cog, description="preset image editor"):


    def __init__(self, cli):
        self.cli = cli
        self.captionGenerator = caption_generator.CaptionGenerator("./resources/fonts/impact.ttf")
        self.soyPhoneImage = Image.open("./resources/this_image/soyphone.png")


    @commands.group(name='this')
    async def this(self, ctx):
        if ctx.invoked_subcommand is None:
            # get the group and methods of this cog
            groupObj = ctx.cog.walk_commands()
            helpObj = CustomHelpCommand()
            helpObj.context = ctx
            await helpObj.send_group_help(next(groupObj))


    @this.command(name="leme", description="This is leme.")
    async def leme(self, ctx):
        img, ext = await util.get_last_img(ctx, 6) 
        if ext == -1: return 0
        capImg = self.captionGenerator.multiline_caption(img, "THIS IS LEME")
        await ctx.channel.send(file=await util.PIL_img_to_file(ctx, capImg, ext)) 

    @this.command(name="soyphone", description="Soyphone reaction.")
    async def soyphone(self, ctx):
        img, ext = await util.get_last_img(ctx, 6)
        cv2_img = numpy.asarray(img)
        cv2_img = util.resize_img_cv2(cv2_img, width = 243)
        height, width, x = cv2_img.shape
        #crop image if too long
        if height > 430:
            height = 430
            cv2_img = cv2_img[0:height, 0:width]    
        
        offsetx1, offsety1 = self.get_offset_cords(23, 84, 265, 64, (430/2) - (height/2), 37, 430)
        offsetx2, offsety2 = self.get_offset_cords(23, 84, 265, 64, (430/2) + (height/2), 37, 430)

        
        transform_pt = numpy.float32([[23 + offsetx1, 84 + offsety1],     # top left
                                      [265 + offsetx1, 64 + offsety1],    # top right
                                      [23 + offsetx2, 84 + offsety2],     # bottom left
                                      [265 +  offsetx2, 64 + offsety2]])  # bottom right

        original_pt = numpy.float32([[0, 0],             # top left
                                     [width, 0],         # top right
                                     [0, height],        # bottom left
                                     [width, height]])   # bottom right
        matrix = cv2.getPerspectiveTransform(original_pt, transform_pt)
        warpedImg = cv2.warpPerspective(cv2_img, matrix, (680, 593))

        # fix if image doesnt have an alpha channel
        # get the rgb channel for the image
        b_channel, g_channel, r_channel = cv2.split(warpedImg)[:3]
        # create a dummy alpha channel
        alpha_channel = numpy.ones(b_channel.shape, dtype=b_channel.dtype) * 50
        # merge the 3 channels and dummy alpha channel, now this image has an alpha channel!
        warpedImg = cv2.merge((b_channel, g_channel, r_channel, alpha_channel))

        trans_mask = warpedImg[:,:,3] == 0
        warpedImg[trans_mask] = [255, 255, 255, 255]
        finalImg = cv2.cvtColor(warpedImg, cv2.COLOR_BGRA2BGR)
        PILImg = Image.fromarray(finalImg)
        PILImg.paste(self.soyPhoneImage, (0, 0), self.soyPhoneImage)
        await util.send_PIL_img(ctx, PILImg, ext)


    def get_offset_cords(self, x1, y1, x2, y2, hypotenuse, adjacentSide, oppositeSide):
        deltax = x2 - x1
        deltay = y2 - y1
        angle = numpy.tan(adjacentSide/oppositeSide)
        offsetx = numpy.sin(angle)*hypotenuse
        offsety = numpy.cos(angle)*hypotenuse
        return offsetx, offsety


async def setup(client):
    await client.add_cog(ThisImage(client))