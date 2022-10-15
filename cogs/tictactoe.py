
from help import CustomHelpCommand
from discord.ext import commands, tasks
from util import PIL_img_to_file
from tic_tac_toe.tic_tac_toe_logic import TicTacToeLogic

class TicTacToe(commands.Cog, description="tictactoe commands"):


    def __init__(self, client):
        #               [0]       [1]        [2]          [3]             [4]        [5]     [6]
        # format ex: ["guild", player1ID, player2ID, TicTacToeLogic, gamemessage, complete, task]
        self.activeGameList = []
        self.client = client
        self.inputToCords = {'1' : (0, 0), '2' : (1, 0), '3' : (2, 0), 
                            '4' : (0, 1), '5' : (1, 1), '6' : (2, 1), 
                            '7' : (0, 2), '8' : (1, 2), '9' : (2, 2)}


    @commands.group(name='ttt')
    async def ttt(self, ctx):
        if ctx.invoked_subcommand is None:
            # get the group and methods of this cog
            groupObj = ctx.cog.walk_commands()
            helpObj = CustomHelpCommand()
            helpObj.context = ctx
            await helpObj.send_group_help(next(groupObj))


    @ttt.command(name="move", description="Place an X or O on the board at pos[1-9] inclusive.")
    async def move(self, ctx, pos):

        #convert pos to x y
        x, y = self.inputToCords[pos]


        player = str(ctx.author)
        playerName = player[:-5]
        msg = ctx.message
        # check if there is an active game on the guild
        game = self.get_game(ctx, True)

        # found the game
        # check if author is player1
        if game[1] == player and game[3].can_make_move("x"):
            # game host making move
            if game[3].player_move(x, y, "x"):
                await self.game_over(ctx, game, f"{playerName} wins!")
                game[5] = True
            await msg.delete()
        elif game[2] == player and game[3].can_make_move("o"):
            # 2nd host making move
            if game[3].player_move(x, y, "o"):
                await self.game_over(ctx, game, f"{playerName} wins!")
                game[5] = True
            await msg.delete()
        elif game[2] == "" and game[1] != player:
            # 2nd player not found yet, set 2nd player
            game[2] = player
            await game[4].edit(content=f"TicTacToe: {game[1][:-5]} vs. {playerName}")
            if game[3].player_move(x, y, "o"):
                await self.game_over(ctx, game, f"{playerName} wins!")
                game[5] = True
            await msg.delete()
        else:
            return
        if game[3].board_full() and game[5] != True:
            await self.game_over(ctx, game, f"{game[1][:-5]} and {game[2][:-5]} tied!")

        await self.update_visual(ctx, game[3].boardVisual.boardImage, game)
        

    @ttt.command(name="quit", description="Ends the current game you are playing.")
    async def quit(self, ctx):
        player = str(ctx.author)
        # check if there is an active game on the guild
        game = self.get_game(ctx)
        if game is not None and (game[1] == player or game[2] == player):
            await game[4].edit(content=f"TicTacToe: Game over, {str(ctx.author)[:-5]} quit.")
            game[6].cancel()
            self.activeGameList.remove(game)


    async def timeout(self, ctx, game):
        if game[6].current_loop == 1:
            await self.game_over(ctx, game, f"time ran out.")


    async def game_over(self, ctx, game, reason):
        player = str(ctx.author)
        rsnStr = f"TicTacToe: Game over, " + reason
        await game[4].edit(content=rsnStr)
        # check if there is an active game on the guild
        game = self.get_game(ctx)
        if game is not None and (game[1] == player or game[2] == player):
            self.activeGameList.remove(game)
            game[6].cancel()
        

    async def update_visual(self, ctx, img, game):
        if game[4] is None:
            game[4] = await ctx.send(f"TicTacToe: {str(ctx.author)[:-5]} has started a new game. Anyone can make a move to join!")
        await game[4].add_files(await PIL_img_to_file(ctx, game[3].boardVisual.boardImage, "png"))
        


    def get_game(self, ctx, create=False):
        # check if there is an active game on the guild
        for game in self.activeGameList:
            if game[0] == ctx.guild:
                return game
        # game DNE, create one and get it
        if create:
            self.create_game(ctx)
            return self.get_game(ctx)
        else:
            return None


    def create_game(self, ctx):
        timeoutTask = tasks.loop(seconds=300, count=2)(self.timeout)
        self.activeGameList.append([ctx.guild, str(ctx.author), "", TicTacToeLogic(), None, False, timeoutTask])
        self.activeGameList[-1][6].start(ctx, self.activeGameList[-1])


async def setup(client):
    await client.add_cog(TicTacToe(client))
