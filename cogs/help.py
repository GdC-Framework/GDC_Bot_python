import itertools

from discord import Embed, Color
from discord.ext import commands
from discord.ext.commands import Context

import discord.utils
from typing import Mapping, Optional, List, Any, TYPE_CHECKING
from discord.ext.commands.cog import Cog
from discord.ext.commands.core import Group, Command, get_signature_parameters
from discord.ext.commands.errors import CommandError


from utils import config

cfg = config.Config()


class MyHelpCommand(commands.MinimalHelpCommand):

    def __init__(self, **options):
        super().__init__(**options)
        self.sort_commands

    async def send_pages(self):
        destination = self.get_destination()
        e = Embed(color=Color.blurple(), description='')
        for page in self.paginator.pages:
            e.description += page
        await destination.send(embed=e)

    # async def send_bot_help(self, mapping: Mapping[Optional[Cog], List[Command[Any, ..., Any]]], /) -> None:
    async def send_bot_help(self, mapping, /) -> None:
        ctx = self.context
        bot = ctx.bot

        if bot.description:
            self.paginator.add_line(bot.description, empty=True)

        note = self.get_opening_note()
        if note:
            self.paginator.add_line(note, empty=True)

        no_category = f'\u200b{self.no_category}'

        def get_category(command, *, no_category: str = no_category) -> str:
            cog = command.cog
            return cog.qualified_name if cog is not None else no_category

        filtered = await self.filter_commands(bot.commands, sort=True, key=get_category)
        to_iterate = itertools.groupby(filtered, key=get_category)

        for category, commands in to_iterate:
            # n'affiche pas les commandes sans catégorie
            if category == "​No Category":
                continue
            commands = sorted(commands, key=lambda c: c.name) if self.sort_commands else list(commands)
            self.add_bot_commands_formatting(commands, category)

        note = self.get_ending_note()
        if note:
            self.paginator.add_line()
            self.paginator.add_line(note)

        await self.send_pages()


class Help(commands.Cog, name="Help"):
    def __init__(self, bot):
        self.bot = bot
        self.bot.help_command.verify_checks = False
        self.bot.help_command = MyHelpCommand()


async def setup(bot):
    bot.logger.info("Loading 'help'")
    await bot.add_cog(Help(bot))
