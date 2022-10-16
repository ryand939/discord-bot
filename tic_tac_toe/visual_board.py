from PIL import Image, ImageDraw, ImageFont

class VisualBoard:


    def __init__(self):
        # got the board image from google images
        self.boardImage = Image.open("./resources/tictactoe/board_label.png")
        self.font = ImageFont.truetype(font="./resources/fonts/cour.ttf", size=200)
        self.draw = ImageDraw.Draw(self.boardImage)


    def draw_symbol(self, x, y, symbol):
        x = 8 + 122*x
        y = -58 + 123*y
        dimensions = self.font.getbbox(symbol)
        self.draw.rectangle((x + 30, y + 58 + 30, x + self.font.getlength(symbol) - 30, y + self.font.getlength(symbol) + 58 - 30), fill='white')
        self.draw.text((x, y), symbol, font=self.font, fill=(0, 0, 0, 128))

    
    def get_image(self):
        return self.boardImage

