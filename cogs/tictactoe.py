
import discord
from help import CustomHelpCommand
from discord.ext import commands
from tic_tac_toe.board import Board
from tic_tac_toe.tic_tac_toe_logic import TicTacToeLogic

class TicTacToe(commands.Cog, description="tictactoe commands"):


    def __init__(self, cli):
        #               [0]        [1]          [2]          [3]
        # format ex: ["guild", "player1ID", "player2ID", TicTacToeLogic]
        self.activeGameList = []



    @commands.group(name='ttt')
    async def ttt(self, ctx):
        if ctx.invoked_subcommand is None:
            # get the group and methods of this cog
            groupObj = ctx.cog.walk_commands()
            helpObj = CustomHelpCommand()
            helpObj.context = ctx
            await helpObj.send_group_help(next(groupObj))


    @ttt.command(name="move", description="Place an X or O on the board.")
    async def move(self, ctx, x: int, y: int):
        player = ctx.author.id
        # check if there is an active game on the guild

        game = self.get_game(ctx)

        print("Picked up game in:", game[0])
        # found the game
        # check if author is player1
        if game[1] == player and game[3].can_make_move("x"):
            # game host making move
            game[3].player_move(x, y, "x")
        elif game[2] == player and game[3].can_make_move("o"):
            # 2nd host making move
            game[3].player_move(x, y, "o")
        elif game[2] == "" and game[1] != player:
            # 2nd player not found yet, set 2nd player
            game[2] = player
            game[3].player_move(x, y, "o")

        

        

    @ttt.command(name="quit", description="Ends the current game you are playing.")
    async def quit(self, ctx):
        player = ctx.author.id
        # check if there is an active game on the guild
        game = self.get_game(ctx)
        if game[1] == player or game[2] == player:
            self.activeGameList.remove(game)
        


    def get_game(self, ctx):
        player = ctx.author.id
        # check if there is an active game on the guild
        for game in self.activeGameList:
            if game[0] == ctx.guild:
                return game
        # game DNE, create one and get it
        self.create_game(ctx)
        return self.get_game(ctx)


    def create_game(self, ctx):
        self.activeGameList.append([ctx.guild, ctx.author.id, "", TicTacToeLogic(Board())])

async def setup(client):
    await client.add_cog(TicTacToe(client))