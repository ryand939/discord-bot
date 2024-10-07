# gamble_base.py
import discord
from discord.ext import commands
from typing import List, Optional, Union
import util  
from bank import Bank

class GambleGame:
    def __init__(self, ctx: commands.Context, bet: int, game_name: str): 
        self.ctx = ctx
        self.author = ctx.author
        self.bet = bet
        self.game_name = game_name
        self.bank = Bank()

    async def validate_bet_range(self, min_amount: Optional[int] = None, max_amount: Optional[int] = None) -> bool: 
        # check for positive bet
        if self.bet <= 0:
            await self.send_embed(
                title="Invalid Bet Amount",
                description="Your bet must be a positive number.",
                embed_type="error",
                delete_after=5
            )
            return False

        # check minimum bet
        if min_amount is not None and self.bet < min_amount:
            await self.send_embed(
                title="Bet Too Low",
                description=f"You must bet at least `{min_amount}` daercoin to play.",
                embed_type="error",
                delete_after=8
            )
            return False

        # check maximum bet
        if max_amount is not None and self.bet > max_amount:
            capped_bet = max_amount
            old_bet = self.bet
            self.bet = capped_bet  # cap the bet
            await self.send_embed(
                title="Bet Capped",
                description=f"A `{max_amount}` DC bet offers the highest odds for `{util.get_command_text(self.ctx)}`, so your `{old_bet}` DC bet "
                            f"has been capped to the maximum bet of `{max_amount}` daercoin.",
                embed_type="info",
                delete_after=8
            )

        return True

    async def attempt_withdraw_bet(self) -> bool: 
        success = await self.bank.withdraw(self.ctx.guild.id, self.author.id, self.bet)
        if not success:
            balance = await self.bank.balance(self.ctx.guild.id, self.author.id)
            await self.send_embed(
                title="Insufficient Funds",
                description=f"You do not have enough daercoin to make a `{self.bet}` DC bet.\nYour current balance is `{balance}` DC.",
                embed_type="error",
                delete_after=8
            )
            return False
        return True

    async def validate_input(self, input_value: Union[str, float, int], valid_options: List[Union[str, float, int]]) -> bool: 
        if input_value not in valid_options:
            valid_opts = ', '.join(f"`{opt}`" for opt in valid_options)
            await self.send_embed(
                title="Invalid Input",
                description=f"Your input `{input_value}` is not among the valid options for {self.game_name}. Valid options include: {valid_opts}.",
                embed_type="error",
                delete_after=8
            )
            return False
        return True

    async def validate_guess(self, guess: float, min_guess: Optional[float] = None) -> bool: 
        if min_guess is not None and guess <= min_guess:
            await self.send_embed(
                title="Invalid Guess",
                description=f"Your guess must be above `{min_guess}`.",
                embed_type="error",
                delete_after=8
            )
            return False
        return True


    async def send_embed(self, title: str, description: str, embed_type: str, delete_after: Optional[int] = None): 
        if embed_type == "error":
            color = util.failure_red
            author_field_subject = "Gamble Error"
            footer_text = util.get_command_text(self.ctx, with_all_params=True)
        elif embed_type == "info":
            color = util.default_blue
            author_field_subject = "Gamble Info"
            footer_text = util.get_command_text(self.ctx)
        elif embed_type == "fatal":
            color = util.default_blue
            author_field_subject = "Error"
            footer_text = "Tell daer something is wrong"
        else:
            color = util.default_blue
            author_field_subject = "Gamble"
            footer_text = util.get_command_text(self.ctx)

        embed = discord.Embed(
            description=description,
            color=color,
            timestamp=discord.utils.utcnow()
        )
        embed.set_author(
            name=f"{author_field_subject}: {title}",
            icon_url=self.author.avatar.url if self.author.avatar else None
        )
        embed.set_footer(text=footer_text)
        await self.ctx.send(embed=embed, delete_after=delete_after)

    async def payout(self, amount: int): 
        await self.bank.deposit(self.ctx.guild.id, self.author.id, amount)
