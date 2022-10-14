from .board import Board


class TicTacToeLogic:


    def __init__(self, board=None):
        if board is None: self.board = Board()
        else: self.board = board


    def check_horizontal_winner(self, symbol):
        brd = self.board.gameBoard
        for x in range(0, len(brd)):
            if brd[x][0] == symbol and brd[x].count(symbol) == len(brd[x]):
                return True
        return False


    def check_vertical_winner(self, symbol):
        brd = self.board.gameBoard
        for y in range(0, len(brd)):
            if brd[0][y] == symbol and brd[1][y] == symbol and brd[2][y] == symbol:
                return True
        return False


    def check_diagonal_winner(self, symbol):
        brd = self.board.gameBoard
        if (brd[0][0] == symbol and brd[1][1] == symbol and brd[2][2] == symbol or
            brd[0][2] == symbol and brd[1][1] == symbol and brd[2][0] == symbol):
            return True
        return False

    
    def get_num_symbol(self, symbol):
        brd = self.board.gameBoard
        counter = 0
        for x in range(0, len(brd)):
            for y in range(0, len(brd)):
                if brd[x][y] == symbol:
                    counter += 1
        return counter


    def check_winner(self, symbol):
        return (self.check_horizontal_winner(symbol) or 
                self.check_vertical_winner(symbol) or
                self.check_diagonal_winner(symbol))


    def new_game(self):
        self.board = Board()

    def can_make_move(self, symbol):
        numX = self.get_num_symbol("x")
        numO = self.get_num_symbol("o")
        print(f"numX: {numX}, numO: {numO}")
        if symbol == "x" and (numX - numO) == 0: return True
        elif symbol == "o" and (numX - numO) == 1: return True
        else: return False

    def player_move(self, x, y, symbol):
        if self.board.get_tile(x, y) is None:
            self.board.set_tile(x, y, symbol)