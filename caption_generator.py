import math
from PIL import Image, ImageFont, ImageDraw


class CaptionGenerator:


    def __init__(self, typeFont):
        self.typeFont = typeFont


    # gets the x value that would put the string in the center of the image
    def get_center_x(self, multiLineStr, imgWidth, font):
        largestStr = 0
        largestFound = 0
        for x in range(0, len(multiLineStr)):
            if font.getlength(multiLineStr[x]) > largestFound:
                largestFound = font.getlength(multiLineStr[x])
                largestStr = x

        # x cords are taken from the top left of the string bounding box
        return (imgWidth / 2) - font.getlength(multiLineStr[largestStr]) / 2


    # gets the y offset for bottom text, accounting for multiline strings
    def get_y_offset(self, multiLineStr, font):
        number = 0
        for x in range(0, len(multiLineStr)):
            number += font.getbbox(multiLineStr[x])[3] + 1
        return number


    # draws a "border" for text to be written over
    def caption_border(self, x, y, caption, font, draw):
        borderSize = math.ceil(0.03*font.size)
        draw.text((x - borderSize, y - borderSize), caption, font=font, fill=(0, 0, 0, 255), align="center", spacing=1)
        draw.text((x + borderSize, y - borderSize), caption, font=font, fill=(0, 0, 0, 255), align="center", spacing=1)
        draw.text((x - borderSize, y + borderSize), caption, font=font, fill=(0, 0, 0, 255), align="center", spacing=1)
        draw.text((x + borderSize, y + borderSize), caption, font=font, fill=(0, 0, 0, 255), align="center", spacing=1)


    # formats a string such that it does not run off screen
    def get_multiline_string(self, caption, font, maxWidth):
        textWidth = 0
        words = caption.split(" ")
        wordLen = len(words)
        newStr = ""

        # build the string word by word, and check if it's length is longer than img width
        for x in range(0, wordLen):
            textWidth += font.getlength(words[x] + " ")
            if textWidth >= maxWidth and len(newStr) != 0: # and newStr[-1] != "\n"
                textWidth = font.getlength(words[x] + " ")
                newStr += "\n"
                font.size -= 7 # slightly decrease font size everytime newline added
            newStr += words[x] + " "

        return newStr[:-1]


    # puts the specified text on an image. Bottom text is optional
    def multiline_caption(self, img, captionTop, captionBottom=None):
        draw = ImageDraw.Draw(img)
        newFont = ImageFont.truetype(font=self.typeFont, size=((img.height+img.width)//2)//10)
        margin = math.ceil(0.02*img.height)

        # top text
        newCaptionTop = self.get_multiline_string(captionTop, newFont, img.width)
        x = self.get_center_x(newCaptionTop.split(" \n"), img.width, newFont)
        y = 0
        self.caption_border(x, y, newCaptionTop, font=newFont, draw=draw)
        draw.text((x, y), newCaptionTop, font=newFont, align="center", spacing=1)

        # bottom text
        if captionBottom is not None:
            newCaptionBottom = self.get_multiline_string(captionBottom, newFont, img.width)
            x_bottom = self.get_center_x(newCaptionBottom.split("\n"), img.width, newFont)
            y_bottom = img.height - margin - self.get_y_offset(newCaptionBottom.split("\n"), newFont)
            self.caption_border(x_bottom, y_bottom, newCaptionBottom, font=newFont, draw=draw)
            draw.text((x_bottom, y_bottom), newCaptionBottom, font=newFont, align="center", spacing=1)

        return img

