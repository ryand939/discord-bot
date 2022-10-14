





# this file will represent the current state of the board

class Board:

    def __init__(self):
        self.gameBoard = [[None, None, None], 
                            [None, None, None], 
                            [None, None, None]]

    
    def reset_board(self):
        self.gameBoard = [[None, None, None], 
                          [None, None, None], 
                          [None, None, None]]


    def set_tile(self, x, y, type):
        self.gameBoard[y][x] = type
        print(f"Tile set at x: {x}, y: {y}\n{self.to_string()}")
        
    def get_tile(self, x, y):
        return self.gameBoard[y][x]

    def to_string(self):
        rtnStr = ""
        for x in range(0, len(self.gameBoard)):
            for y in range(0, len(self.gameBoard[0])):
                rtnStr += str(self.gameBoard[x][y]) + "\t"
            rtnStr += "\n"

        return rtnStr
