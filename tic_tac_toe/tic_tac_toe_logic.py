

from .visual_board import VisualBoard


class TicTacToeLogic:

    def __init__(self):
        
        self.boardVisual = VisualBoard()

        self.gameBoard = [[None, None, None], 
                            [None, None, None], 
                            [None, None, None]]


    def check_horizontal_winner(self, symbol):
        brd = self.gameBoard
        for x in range(0, len(brd)):
            if brd[x][0] == symbol and brd[x].count(symbol) == len(brd[x]):
                return True
        return False


    def check_vertical_winner(self, symbol):
        brd = self.gameBoard
        for y in range(0, len(brd)):
            if brd[0][y] == symbol and brd[1][y] == symbol and brd[2][y] == symbol:
                return True
        return False


    def check_diagonal_winner(self, symbol):
        brd = self.gameBoard
        if (brd[0][0] == symbol and brd[1][1] == symbol and brd[2][2] == symbol or
            brd[0][2] == symbol and brd[1][1] == symbol and brd[2][0] == symbol):
            return True
        return False

    
    def get_num_symbol(self, symbol):
        brd = self.gameBoard
        counter = 0
        for x in range(0, len(brd)):
            for y in range(0, len(brd)):
                if brd[x][y] == symbol:
                    counter += 1
        return counter

    
    def board_full(self):
        return ((self.get_num_symbol("o") + self.get_num_symbol("x")) == 9)


    def check_winner(self, symbol):
        return (self.check_horizontal_winner(symbol) or 
                self.check_vertical_winner(symbol) or
                self.check_diagonal_winner(symbol))
        

    # not necessary but I am used to java oop
    def get_tile(self, x, y):
        return self.gameBoard[y][x]


    # not necessary but I am used to java oop
    def set_tile(self, x, y, type):
        self.gameBoard[y][x] = type



    # returns string representation of board
    def to_string(self):
        rtnStr = ""
        for x in range(0, len(self.gameBoard)):
            for y in range(0, len(self.gameBoard[0])):
                rtnStr += str(self.gameBoard[x][y]) + "\t"
            rtnStr += "\n"
        return rtnStr
        


    # determines if a certain symbol can make a move 
    def can_make_move(self, symbol):
        numX = self.get_num_symbol("x")
        numO = self.get_num_symbol("o")
        if symbol == "x" and (numX - numO) == 0: return True
        elif symbol == "o" and (numX - numO) == 1: return True
        else: return False


    # simulates player move on board, returns true if the move caused a win
    def player_move(self, x, y, symbol):
        if self.get_tile(x, y) is None:
            self.boardVisual.draw_symbol(x, y, symbol)
            self.set_tile(x, y, symbol)
        return self.check_winner(symbol)