
from help import invoke_group_help
from discord.ext import commands, tasks
from util import PIL_img_to_file, get_url_for_image
from tic_tac_toe.tic_tac_toe_logic import TicTacToeLogic
from discord import Embed

class TicTacToe(commands.Cog, description="play tictactoe"):


    def __init__(self, client):
        #               [0]       [1]        [2]          [3]             [4]             [5]            [6]
        # format ex: ["guild", player1ID, player2ID, TicTacToeLogic, gameChatMessage, completeBool, timeoutTask]
        self.activeGameList = []
        self.client = client
        self.inputToCords = {'1' : (0, 0), '2' : (1, 0), '3' : (2, 0), 
                             '4' : (0, 1), '5' : (1, 1), '6' : (2, 1), 
                             '7' : (0, 2), '8' : (1, 2), '9' : (2, 2)}


    @commands.hybrid_group(name='ttt')
    async def ttt(self, ctx):
        if ctx.invoked_subcommand is None:
            await invoke_group_help(ctx.cog.walk_commands(), ctx)


    # user command to make a TTT move
    @ttt.command(name="move", description="Make a move at pos[1-9].")
    async def move(self, ctx, pos: str):
        x, y = self.inputToCords[pos]      # convert pos to x y
        player = str(ctx.author)           # player names are stored name#0000
        playerName = player[:-5]           # player names are displayed without tag
        game = self.get_game(ctx, True)    # find the game or create new
        
        # case author is player 1
        if game[1] == player and game[3].can_make_move("x") and game[3].get_tile(x, y) is None:
            if game[3].player_move(x, y, "x"):
                game[4].embeds[0].set_field_at(0, name="Winner", value=f"```{playerName}```")
                game[4].embeds[0].set_field_at(1, name="Loser", value=f"```{game[2][:-5]}```")
                await self.game_over(ctx, game, f"{playerName} wins!")
                game[5] = True
        # case author is player 2
        elif game[2] == player and game[3].can_make_move("o") and game[3].get_tile(x, y) is None:
            if game[3].player_move(x, y, "o"):
                game[4].embeds[0].set_field_at(0, name="Winner", value=f"```{playerName}```")
                game[4].embeds[0].set_field_at(1, name="Loser", value=f"```{game[1][:-5]}```")
                await self.game_over(ctx, game, f"{playerName} wins!")
                game[5] = True
        # case no player 2, author is now player 2
        elif game[2] == "" and game[1] != player and game[3].get_tile(x, y) is None:
            print("here")
            game[2] = player
            game[4].embeds[0].set_field_at(1, name="Player 2", value=f"```{playerName}```")
            game[4].embeds[0].set_footer(text=f"Command: {ctx.bot.command_prefix}ttt move {{number}}")
            if game[3].player_move(x, y, "o"):
                await self.game_over(ctx, game, f"{playerName} wins!")
                game[5] = True
        # case author is not player 1/2, do nothing
        else:
            return

        if ctx.interaction is None: 
            await ctx.message.delete()
        else: await ctx.send("Move successful!", ephemeral=True, delete_after=1)

        # move completed, check fullness of board
        if game[3].board_full() and game[5] != True:
            await self.game_over(ctx, game, f"{game[1][:-5]} and {game[2][:-5]} tied!")
        # update gameMessage embed
        await self.update_visual(ctx, game)

    
    # user command to resend the game message in chat
    # useful when the message gets too far up the message feed
    @ttt.command(name="resend", description="Resend game in chat.")
    async def resend(self, ctx):
        game = self.get_game(ctx)   # get the game in the guild
        player = str(ctx.author)
        # confirm author is one of the two players, then delete current game board and send it again
        if game is not None and (game[1] == player or game[2] == player):
            saveEmbed = game[4].embeds[0]
            await game[4].delete()
            game[4] = await ctx.send(embed=saveEmbed)

            

        
        
    # user command to quit/end the current game
    @ttt.command(name="quit", description="Ends the current game.")
    async def quit(self, ctx):
        player = str(ctx.author)
        # get the current active game if it exists
        game = self.get_game(ctx)
        # confirm author is one of the two players, then quit
        if game is not None and (game[1] == player or game[2] == player):
            game[4].embeds[0].insert_field_at(0, name="Game over", value=f"{str(ctx.author)[:-5]} quit.", inline=False)
            if ctx.interaction is not None:
                await self.resend(ctx)
            else:
                await game[4].edit(embed=game[4].embeds[0])
            game[6].cancel()
            self.activeGameList.remove(game)


    # this function gets ran on a loop seconds=300 iterations=2
    # once the first iteration completes, the second is cancelled immediately and the game is ended
    # so in effect its a 300s timeout
    async def timeout(self, ctx, game):
        if game[6].current_loop == 1:
            await self.game_over(ctx, game, f"time ran out.")


    # method to end a game with a given reason
    async def game_over(self, ctx, game, reason):
        player = str(ctx.author)
        game[4].embeds[0].insert_field_at(0, name="Game over", value=reason, inline=False)
        await game[4].edit(embed=game[4].embeds[0])
        # check if there is an active game on the guild
        game = self.get_game(ctx)
        if game is not None and (game[1] == player or game[2] == player):
            game[6].cancel()
            self.activeGameList.remove(game)
        

    # refreshes the embed at the end of a new move
    async def update_visual(self, ctx, game):
        if game[4] is None:
            gameEmbed = Embed(title="TicTacToe", color=0x3897f0)
            gameEmbed.add_field(name="Player 1", value=f"```{str(ctx.author)[:-5]}```", inline=True)
            gameEmbed.add_field(name="Player 2", value="```Empty```", inline=True)
            gameEmbed.set_footer(text=f"Type {ctx.bot.command_prefix}ttt move {{number}} to join the game! ")
            gameEmbed.set_image(url=await get_url_for_image(ctx, await PIL_img_to_file(ctx, game[3].boardVisual.boardImage, "PNG")))
            game[4] = await ctx.send(embed=gameEmbed)
        else:
            game[4].embeds[0].set_image(url=await get_url_for_image(ctx, await PIL_img_to_file(ctx, game[3].boardVisual.boardImage, "PNG")))
            await game[4].edit(embed=game[4].embeds[0])

        

    # gets the current game in the guild
    # optional boolean to create a game if none is found
    def get_game(self, ctx, create=False):
        for game in self.activeGameList:
            if game[0] == ctx.guild:
                return game
        if create:
            self.create_game(ctx)
            return self.get_game(ctx)
        else:
            return None


    # creates a new game for a guild, and adds its info to the activeGameList
    def create_game(self, ctx):
        timeoutTask = tasks.loop(seconds=300, count=2)(self.timeout)
        self.activeGameList.append([ctx.guild, str(ctx.author), "", TicTacToeLogic(), None, False, timeoutTask])
        self.activeGameList[-1][6].start(ctx, self.activeGameList[-1])



async def setup(client):
    await client.add_cog(TicTacToe(client))
