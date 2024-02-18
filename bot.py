#!/usr/bin/env python3
# -*- coding: utf8 -*-

import os
import asyncio

import logging
from logging.handlers import RotatingFileHandler
try:
    from cysystemd.journal import JournaldLogHandler
except ImportError:
    JournaldLogHandler = None

import random
from datetime import datetime
from time import time

import discord
from discord.ext import commands, tasks
from discord.flags import Intents

from utils import config, database, mail
from utils.config import bot_configuration as cfg

messages = config.Messages()
mail = mail.Mail(cfg)

# Get pid and check if bot is already running, to get only 1 instance
# pidBot = pid.PID
# pidBot.check_launch(pidBot, os.getpid())


class MyBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Put db has a bot object to reduce connection number, instead of initiating db in each needed cog
        self.db = database.Database(cfg)
        self.bot_data = config.Data()

        statuses = hasattr(self.bot_data, "messages") and self.bot_data.messages or None
        self.statuses = (statuses is not None and len(statuses) > 0) and statuses or ["Datas error"]
        self.embed_colors = {"ERROR": discord.Color.brand_red(),
                             "INFO": discord.Color.gold(),
                             "SUCCESS": discord.Color.green()}

    # region Custom function

    async def load_cogs(self):
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    await self.load_extension(f"cogs.{extension}")
                    self.logger.info(f"Loaded extension '{extension}'")

                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    self.logger.info(
                        f"Failed to load extension {extension}\n{exception}"
                    )

    async def send_moderation_message(
        self, concerning="Message", message_type="Error", message="Message"
    ):
        """custom function to send embed"""
        for guild in self.guilds:
            channel = discord.utils.get(
                guild.channels, id=self.bot_data.moderation_channel
            )
            if channel:
                break
        if not channel:
            message += "\nModeration channel not found"
            self.logger.error(f"{message}")
            channel = guild.system_channel

        changed = False
        for info in my_bot.db.db_info:
            if info != "connect_timeout" and str(my_bot.db.db_info[info]) in message:
                changed = True
                last_char = (
                    4
                    if str(my_bot.db.db_info[info]).__len__() >= 4
                    else str(my_bot.db.db_info[info]).__len__()
                )
                message = message.replace(
                    str(my_bot.db.db_info[info]),
                    str(my_bot.db.db_info[info])[:-last_char] + "\*" * last_char,
                )

        message += " (see logs for more details)" if changed else ""

        embed = discord.Embed(
            title=f"{concerning} {message_type}",
            description=message,
            color=self.embed_colors[(message_type.split(" "))[0].upper()]
            or discord.Color.dark_teal(),
            timestamp=datetime.now(),
        )
        await channel.send(embed=embed)

    # endregion

    # The code in this event is executed when the bot is ready
    async def on_ready(self):
        self.logger.debug(self.guilds)
        self.logger.debug([role for role in [guild.roles for guild in self.guilds]])
        await self.load_cogs()
        self.logger.info("My Ready is Body")
        self.logger.info(f"{self.user} is connected to the following guild:")
        for guild in self.guilds:
            self.logger.info(f"\t{guild.name}(id: {guild.id})")
        status_task.start()

    # The code in this event is executed every time someone sends a message, with or without the prefix
    async def on_message(self, message: discord.Message):
        pref = cfg.prefix
        if "<@" + str(self.user.id) + ">" in message.content.lower():
            await message.channel.send(
                f"On parle de moi ! Pour avoir plus d'informations, tape {pref}help"
            )
        # Ignores if a command is being executed by a bot or by the bot itself
        if message.author == self.user or message.author.bot:
            return
        await self.process_commands(message)

    # The code in this event is executed every time a normal command has been *successfully* executed
    async def on_command_completion(self, ctx):
        full_command_name = ctx.command.qualified_name
        split = full_command_name.split(" ")
        executed_command = str(split[0])
        kwargs = f" `{ctx.kwargs}`" if ctx.kwargs.__len__() > 0 else ""
        args = (
            f" `{[str(arg) for arg in ctx.args if ctx.args.index(arg) > 1]}`"
            if ctx.args.__len__() > 2
            else kwargs
        )
        self.logger.info(
            f"Executed `{ctx.clean_prefix}{executed_command}`{args} command in {f'{ctx.channel.guild.name} - {ctx.channel.name}' if ctx.channel.guild != None else 'DM' } (ID: {ctx.channel.id}) by {ctx.message.author} (ID: {ctx.message.author.id})"
        )

    # The code in this event is executed every time a normal valid command catches an error
    async def on_command_error(self, context, error):
        send_mail = True
        if isinstance(error, commands.CommandOnCooldown):
            send_mail = False
            minutes, seconds = divmod(error.retry_after, 60)
            hours, minutes = divmod(minutes, 60)
            hours = hours % 24
            embed = discord.Embed(
                title="Hey, please slow down!",
                description=f"You can use this command again in {f'{round(hours)} hours' if round(hours) > 0 else ''} {f'{round(minutes)} minutes' if round(minutes) > 0 else ''} {f'{round(seconds)} seconds' if round(seconds) > 0 else ''}.",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.MissingPermissions):
            send_mail = False
            embed = discord.Embed(
                title="Error!",
                description="You are missing the permission(s) `"
                + ", ".join(error.missing_permissions)
                + "` to execute this command!",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.MissingRequiredArgument) or isinstance(
            error, commands.MissingAnyRole
        ):
            send_mail = False
            embed = discord.Embed(
                title="Error!", description=str(error), color=0xE02B2B
            )
            await context.reply(embed=embed)
        elif isinstance(error, commands.CommandInvokeError):
            send_mail = False
            if "Cannot send messages to this user" in str(error):
                description = (
                    f"I can't send you any private messages :confused: \n{str(error)}"
                )
            else:
                description = f"{str(error)}"
            embed = discord.Embed(
                title="Error!", description=description, color=0xE02B2B
            )
            await context.reply(embed=embed)
        else:
            embed = discord.Embed(
                title="Error!", description=str(error), color=0xE02B2B
            )
            await context.reply(embed=embed)

        # Disconnect DB in case of any error
        try:
            self.db.disconnect()
        except Exception as e:
            ...

        if mail.is_init and send_mail:
            # send mail if unhandled error
            mail.send(
                cfg.gmail_user,
                f"Unhandled error {type(error).__name__}",
                error,
                context,
            )
        self.logger.error(error)
        # raise error


# Defining intents
botIntents = Intents.default()
botIntents.guilds = True
botIntents.messages = True
botIntents.reactions = True
botIntents.message_content = True
botIntents.members = True


my_bot = MyBot(
    command_prefix=cfg.prefix,
    description=cfg.bot_name,
    intents=botIntents,
    owner_id=cfg.id_owner,
)
my_bot.remove_command("help")


# region Logging configuration
class LoggingFormatter(logging.Formatter):
    # Colors
    black = "\x1b[30m"
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    gray = "\x1b[38m"
    # Styles
    reset = "\x1b[0m"
    bold = "\x1b[1m"

    COLORS = {
        logging.DEBUG: gray + bold,
        logging.INFO: blue + bold,
        logging.WARNING: yellow + bold,
        logging.ERROR: red,
        logging.CRITICAL: red + bold,
    }

    def format(self, record):
        log_color = self.COLORS[record.levelno]
        format = "(black){asctime}(reset) (levelcolor){levelname:<8}(reset) (green){name}(reset) {message}"
        format = format.replace("(black)", self.black + self.bold)
        format = format.replace("(reset)", self.reset)
        format = format.replace("(levelcolor)", log_color)
        format = format.replace("(green)", self.green + self.bold)
        formatter = logging.Formatter(format, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)


logger = logging.getLogger("discord_bot")
logger.setLevel(cfg.logger["debugLevel"])

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(LoggingFormatter())
logger.addHandler(console_handler)

# Rotating file handler
rotating_file_handler = RotatingFileHandler(filename=f'logs/{cfg.bot_name}.log', mode="w", maxBytes=cfg.logger["max_bytes"], backupCount=cfg.logger["backup_count"], encoding="utf-8")
rotating_file_formatter = logging.Formatter("%(asctime)s - %(process)d - [%(levelname)s] - %(message)s", datefmt='%y%m%d_%H%M%S')
rotating_file_handler.setFormatter(rotating_file_formatter)
logger.addHandler(rotating_file_handler)

# systemd handler
if JournaldLogHandler:
    journal_handler = JournaldLogHandler()
    syslog_formatter = logging.Formatter(
        "%(asctime)s - %(process)d - [%(levelname)s] - %(message)s",
        datefmt="%y%m%d_%H%M%S",
    )
    journal_handler.setFormatter(syslog_formatter)
    logger.addHandler(journal_handler)

# Add the handlers
my_bot.logger = logger
my_bot.logger.info("--------------------------------------------------")
my_bot.logger.debug(
    f"Loggers : {[type(handler) for handler in my_bot.logger.handlers]}"
)

# endregion


@my_bot.command()
async def disconnect(ctx):
    """
    Disconnect the bot from voice channel
    Should not be used, but we never know ¯\_(ツ)_/¯
    """
    voice = discord.utils.get(my_bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.disconnect()


# Setup the game status task of the my_bot
@tasks.loop(seconds=30)
async def status_task():
    await my_bot.change_presence(
        activity=discord.CustomActivity(random.choice(my_bot.statuses))
    )


@my_bot.listen()
async def on_reaction_add(reaction, user):
    # await reaction.message.channel.send("réaction ajoutée")
    pass


@my_bot.event
async def on_guild_join(guild):
    """Executed when bot join a new guild"""
    my_bot.logger.info(f"Bot joined guild {guild.name}")
    await guild.system_channel.send(
        "Bonjour, c'est le bot LSD python! Je suis là pour vous aider à gérer votre serveur discord. "
    )


@my_bot.event
async def on_member_join(member):
    my_bot.logger.info(f"{member.display_name} joined {member.guild.name}")


@my_bot.event
async def on_raw_member_remove(payload):
    my_bot.logger.info(f"{payload.user.display_name} left {payload.user.guild.name}")


@my_bot.event
async def on_scheduled_event_update(before, after):
    my_bot.logger.debug(f"'Event desc: {before.description} => {after.description}")


if __name__ == "__main__":
    my_bot.logger.info("================== Starting bot ==================")
    my_bot.logger.info(f"discord.py version: {discord.__version__}")
    my_bot.run(cfg.token)
