# russianroulette.py

import discord
from discord import File, Embed
from datetime import timedelta
import asyncio
import numpy as np
import os

# Import utility functions and constants
import util


class RussianRoulette:
    def __init__(self, ctx):
        self.ctx = ctx
        self.author = ctx.author
        self.footer_text = util.get_command_text(ctx)
        self.timeout_minutes = 3
        self.survive_img_path = os.path.join(util.bot_directory, "resources", "misc", "media", "survive_compressed.gif")
        self.die_img_path = os.path.join(util.bot_directory, "resources", "misc", "media", "rip_compressed.gif")
    
    # returns True 1/6 times
    def bullet_in_chamber(self):
        rng = np.random.default_rng()
        chamber = rng.integers(1, 7)  # 1 to 6 inclusive
        return chamber == 1
     


    async def execute(self):
        if self.bullet_in_chamber():
            await self.handle_death()
        else:
            await self.handle_survival()


    # --- CASE THEY SURVIVE ---

    async def handle_survival(self): 
        ctx = self.ctx
        footer_text = self.footer_text
        file = File(self.survive_img_path, filename="survive.gif")
        embed = util.get_embed(title=None,
            attachment="attachment://survive.gif",
            col=util.success_green  # green color for survival
        )
        embed.set_author(
            name=f"{ctx.author.display_name} survived russian roulette!",
            icon_url=ctx.author.avatar.url if ctx.author.avatar else None
        )
        embed.set_footer(text=footer_text)
    
        # send the survival embed immediately
        await ctx.send(file=file, embed=embed)
    

    # --- CASE THEY DIE ---

    async def handle_death(self): 
        ctx = self.ctx
        footer_text = self.footer_text
        file = File(self.die_img_path, filename="rip.gif")

        # INITIAL EMBED SAYING THEYRE ABOUT TO DIE, SHOWS FOR A FEW SECONDS
        embed = util.get_embed(title=None, attachment="attachment://rip.gif", col=util.failure_red)  # Red color for loss
        embed.set_author( name=f"Any last words, {ctx.author.display_name}?", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        embed.set_footer(text=footer_text)
        message = await ctx.send(file=file, embed=embed)
        await asyncio.sleep(4)
    

        # NOW TIME THEM OUT AND UPDATE THE EMBED
        try: await ctx.author.timeout(timedelta(minutes=self.timeout_minutes), reason=f"Russian Roulette.")

            # CANT TIME THEM OUT BECAUSE NO PRIV ?
        except discord.Forbidden:
            print(f"Failed to timeout user {ctx.author.id} in guild {ctx.guild.id}: Missing permissions.")
            warning_embed = util.get_embed(
                title=None,
                content="daerbot does not have permission to time out this user.",
                col=util.failure_red )
            warning_embed.set_author(
                name=f"{ctx.author.display_name} has been saved by lack of permissions",
                icon_url=ctx.author.avatar.url if ctx.author.avatar else None )
            warning_embed.set_footer(text=footer_text)
            embed.set_image(url=None)  # remove original gif
            await message.edit(embed=warning_embed, attachments=[])

            return
        
            # OTHER ERROR IN TIMING THEM OUT ?
        except discord.HTTPException as e:
            print(f"HTTPException while timing out user {ctx.author.id} in guild {ctx.guild.id}: {e}")
            error_embed = util.get_embed(
                title=None,
                content=f"devs fix this shit!!!!\n{e}",
                col=util.failure_red
            )
            error_embed.set_author(
                name=f"{ctx.author.display_name} has been saved by a random error",
                icon_url=ctx.author.avatar.url if ctx.author.avatar else None )
            error_embed.set_footer(text=footer_text)
            
            embed.set_image(url=None)  # remove original gif
            await message.edit(embed=error_embed, attachments=[])
            return
    
        # NOW THEY ARE TIMED OUT
        # EDIT THE ORIGINAL MESSAGE SO EVERYONE KNOWS WHAT HAPPENED
        timeout_embed = util.get_embed(title=None, 
            content=f"{ctx.author.display_name} got unlucky playing russian roulette and has been timed out for {self.timeout_minutes} minutes.",
            col=util.failure_red  # Red color for loss
        )
        timeout_embed.set_author(
            name=f"{ctx.author.display_name} will be back soon",
            icon_url=ctx.author.avatar.url if ctx.author.avatar else None
        )
        timeout_embed.set_footer(text=footer_text)

        if message:
            try: 
                await message.edit(embed=timeout_embed, attachments=[])
            except discord.HTTPException as e:
                print(f"Failed to edit message for {ctx.author.id}: {e}")

