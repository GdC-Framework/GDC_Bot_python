import random
import sys

import datetime

from asyncio import sleep
from discord import TextChannel, Message, Status, Member
from discord.ext import commands
from discord import app_commands
from discord.ext.commands import Context


from utils import checks, database, mail, config

cfg = config.Config()
data = config.Data()

class Moderation(commands.Cog, name="Moderation"):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @commands.command(
        name="tell",
        description="The bot will say anything you want.",
    )
    @commands.has_any_role("Admins")
    async def tell(self, context: Context, *, message: str):
        """
        The bot will say anything you want.
        """
        await context.send(message)

    @commands.command(name="send_message")
    @commands.has_any_role("Admins")
    async def send_message(self, ctx, dest_channel:TextChannel, message):
        """
        Send in the textChannel <dest_channel> the Message <message>
        """
        await dest_channel.send(message)
    
    @commands.command(name="edit_message")
    @commands.has_any_role("Admins")
    @app_commands.describe(orignal_message="url: link to the original message", message="str: New message", append="bool: True or False", add_reaction="emoji: Reaction to add to the message")
    async def edit_message(self, ctx, orignal_message:Message, message: str, append: bool=True, add_reaction=None):
        """
        Edit the <original_message> with <message>. You can <append> it not not, and <add_reaction>
        example : edit_message https://discord.com/channels/123456789012345678/123456789012345678/1234567890123456789 "Hello there" False :sunglasses: 
        """
        if append:
            orignal_message.content=f"{orignal_message.content}\n{message}"
        else:
            orignal_message.content=f"{message}"
        
        await orignal_message.edit(content=orignal_message.content)
        if add_reaction:
            await orignal_message.add_reaction(f"{add_reaction}")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @commands.has_any_role("Admins")
    async def keep_lm(self, ctx, arg: int):
        """
        Keep last <arg> messages in current channel
        Does not delete pinned messages
        """
        nb_msg = int(arg) + 2
        new_message = await ctx.reply('En cours !')
        
        msg_history = [message async for message in ctx.channel.history(limit=1000)]
        msg_history_list = msg_history[nb_msg:]
        msg_pinned = await ctx.channel.pins()
        for msg in msg_history_list:
            if msg not in msg_pinned:
                await msg.delete()
                # attendre que le message soit supprimé
                await sleep(2)
        
        await ctx.message.delete()
        await new_message.delete()
        self.bot.logger.info(f"Suppression de {len(msg_history_list)} messages dans {ctx.channel.name} par {ctx.author.name}")  

async def setup(bot):
    bot.logger.info("Loading 'moderation'")
    await bot.add_cog(Moderation(bot))