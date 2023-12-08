from asyncio import sleep
import discord
from discord.ext import commands
from discord.ext.commands import Context

from utils import checks, config

cfg = config.Config()


class Owner(commands.Cog, name="Owner"):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.bot_data = bot.bot_data

    @commands.command(
        name="sync",
        description="Synchonizes the slash commands.",
    )
    @commands.has_any_role("Admins", "Mission pooler")
    @checks.is_owner()
    async def sync(self, context: Context) -> None:
        """
        Synchonizes the slash commands.
        """
        context.bot.tree.copy_global_to(guild=context.guild)
        await context.bot.tree.sync()
        embed = discord.Embed(
            description="Les commandes slash ont été synchronisées avec succès !",
            color=0x5865F2,
        )
        await context.send(embed=embed)

    @commands.command(name="testing")
    @commands.has_any_role("Admins", "Mission pooler")
    @checks.is_owner()
    async def testing(self, ctx):
        """
        Only used for testing purpose
        """
        message = "This is a test"
        # liste les commandes et leurs permissions
        # list_of_command_perms = []
        # for command in self.bot.commands:
        #     list_of_command_perms.append(f"{command.name} : {command.checks}")
        # message = "\n".join(list_of_command_perms)

        # liste les permissions pour le @commands.has_permissions()
        # list_of_perms = []
        # perms = discord.permissions.Permissions.VALID_FLAGS
        # for perm in perms:
        #     list_of_perms.append(f"{perm} : {perms[perm]}")
        # message = "\n".join(list_of_perms)

        await ctx.reply(message)

    @commands.command(name="status", aliases=["st"])
    @commands.has_any_role("Admins", "Mission pooler")
    @checks.is_owner()
    async def status(self, ctx: Context, action:str="", *strings):
        """
        Update status messages
        action : [add, a], [delete, del, d], [new, n], [view, v]
        *strings : list of message to add or delete

        Usage : 
        `!status`, `!st` > view all statuses
        `!status add "New message"` > add `New message` in the list of statuses (don't forget double quote `"`, simple quote `'` won't work as intended)
        `!status new "Message 1" "Message 2"` > replace previous status messages by "Message 1" and "Message 2"
        `!status del "Message 1"` > delete "Message 1" if it exist in the list, else does nothing. Can delete multiple message at the same time
        """
        updated = True
        message = ""
        statuses = self.bot_data.messages or None
        message = f"Current statuses : {statuses}"
        if action in ["", "view, v"]:
            updated = False
        elif action in ["add", "a"]:
            for arg in strings:
                self.bot_data.messages.append(arg)
        elif action in ["new", "n"]:
            self.bot_data.messages = [arg for arg in strings]
        elif action in ["delete", "del", "d"]:
            for arg in strings:
                if arg in self.bot_data.messages:
                    self.bot_data.messages.remove(arg)
        if updated:
            statuses = self.bot_data.messages or None
            message += f"\nNew statuses : {statuses}"
            self.bot.statuses = (statuses != None and len(statuses) > 0) and statuses or ["made by Basox70", "Data error"]
            self.bot_data.save(self.bot_data)
        await ctx.send(message)

    @commands.command(name="delay", aliases=["grd"])
    @commands.has_any_role("Admins", "Mission pooler")
    @checks.is_owner()
    async def delay(self, ctx: Context, *new_delays:int):
        """
        Update global reminder delays 
        *new_delays : list of new delays (max 3 values in minutes, min value => 15)
        If less than 3 values are set, then the latest reminder will be done
        A delay set to 0 deactivate the reminder (only the last one will be set at 15min)

        Usage : 
        `!delay`, `!grd` > view all delays
        `!delay -1` > reset delays to default [1440, 60, 15] (24h, 1h, 15min)
        `!delay 0` > deactivate reminders
        `!delay 60 30 15` > set delays to 60min, 30min and 15min
        `!delay 60 0 15` > set delays to 60min and 15min. the 2nd reminder is disabled

        """
        updated = True
        default = [1440, 60, 15]
        message = ""
        delays = self.bot_data.event_reminder_delay or None
        message = f"Current delays : {delays}"
        if len(new_delays) == 0:
            updated = False
        else:
            # Si le paramètre est -1, réinitialisation des délais aux valeurs défauts
            if new_delays[0] == -1:
                self.bot_data.event_reminder_delay = default
            else:
                self.bot_data.event_reminder_delay = [arg for arg in new_delays[:3]]
                # Si la dernière valeur est < 15 et différente de 0, alors on met 15 
                if self.bot_data.event_reminder_delay[-1] < 15 and self.bot_data.event_reminder_delay[-1] != 0:
                    self.bot_data.event_reminder_delay[-1] = 15
                # Pour chaque valeur, si c'est < 15, alors on désactive le rappel
                for i in range(0,self.bot_data.event_reminder_delay.__len__()):
                    if self.bot_data.event_reminder_delay[i] < 15:
                        self.bot_data.event_reminder_delay[i] = 0
                # Si il n'y a pas assez de valeurs, on ajoute des valeurs 0 au début du tableau
                if self.bot_data.event_reminder_delay.__len__() < 3:
                    while self.bot_data.event_reminder_delay.__len__() < 3:
                        self.bot_data.event_reminder_delay.insert(0, 0)
        
        if updated:
            delays = self.bot_data.event_reminder_delay or None
            message += f"\nNew delays : {delays}"
            self.bot.event_reminder_delay = (delays != None and len(delays) > 0) and delays or default
            self.bot_data.save(self.bot_data)
        await ctx.send(message)

    @commands.command(name="exit")
    @commands.has_any_role("Admins", "Mission pooler")
    @checks.is_owner()
    async def exit(self, ctx: Context):
        """
        Shutdown the bot
        """
        # await disconnect(ctx)
        # pid_bot = pid.PID
        await ctx.send("Extinction du bot")
        self.bot.logger.info('=== Extinction du bot ===')
        # close database
        self.db.disconnect()
        # change status to offline
        await self.bot.change_presence(status=discord.Status.offline)
        # remove pid file
        # pid_bot.unlink(pid_bot)
        # close bot
        await self.bot.close()

    @commands.command(name="setPrefix")
    @commands.has_any_role("Admins", "Mission pooler")
    @checks.is_owner()
    async def setPrefix(self, ctx):
        """
        ! NOT OPERATIONNAL !
        Send current prefix for the discord guild
        """
        prefix = self.bot.get_prefix(ctx.message)
        await ctx.send('Current prefix is '+prefix)

    @commands.command(name="moderationChannel", aliases=["mod", "modChan", "mc"])
    @commands.has_any_role("Admins", "Mission pooler")
    @checks.is_owner()
    async def moderationChannel(self, ctx, newChannel:discord.TextChannel=None):
        """
        Get or Set Moderation Channel (Channel in which the bot send error or info messages)
        """
        msg = ""
        for guild in self.bot.guilds:
            channel = discord.utils.get(guild.channels, id=self.bot_data.moderation_channel)
        if not channel:
            channel = guild.system_channel
            msg += f"Moderation channel not found, using System channel {channel.mention}"
        else : 
            msg = f'Current Moderation Channel : {channel.mention} ({channel.id})'

        if newChannel:
            msg += f'\nNew Moderation Channel : {newChannel.mention} ({newChannel.id})'
            self.bot_data.moderation_channel = newChannel.id
            self.bot_data.save(self.bot_data)
        await ctx.reply(msg)

    @commands.command(name="cog")
    @commands.has_any_role("Admins", "Mission pooler")
    @checks.is_owner()
    async def cog(self, ctx, option: str="", extension: str="", extras={}):
        """
        Cog management
        """
        if option == "load":
            await self.bot.load_extension(f"cogs.{extension}")
            self.bot.logger.info(f"Loaded cogs.{extension}")
            await ctx.reply(f"Loaded {extension}", delete_after=10)
        elif option == "unload":
            await self.bot.unload_extension(f"cogs.{extension}")
            self.bot.logger.info(f"Unloaded cogs.{extension}")
            await ctx.reply(f"Unloaded {extension}", delete_after=10)
        elif option == "reload":
            await self.bot.reload_extension(f"cogs.{extension}")
            self.bot.logger.info(f"Reloaded cogs.{extension}")
            await ctx.reply(f"Reloaded {extension}", delete_after=10)
        elif option == "list" or option == "get" or option == "":
            await ctx.reply(f"Loaded : {self.bot.cogs.items()}", delete_after=10)
        else:
            await ctx.send('Unknown option. Options are [`get`,`list`], `load`, `reload`, `unload`', delete_after=10)

        # Attendre pendant 10 secondes avant de supprimer le message
        await sleep(10)
        if not ctx.guild:
            await ctx.message.delete()

    @commands.command()
    @commands.has_any_role("Admins", "Mission pooler")
    @checks.is_owner()
    async def get(self, ctx):
        await ctx.reply(f"Loaded : {self.bot.cogs.items()}")

    @commands.command()
    @commands.has_any_role("Admins", "Mission pooler")
    @checks.is_owner()
    async def load(self, ctx, extension, extras={}):
        await self.bot.load_extension(f"cogs.{extension}")
        self.bot.logger.info(f"Loaded cogs.{extension}")
        await ctx.reply(f"Loaded {extension}")

    @commands.command()
    @commands.has_any_role("Admins", "Mission pooler")
    @checks.is_owner()
    async def unload(self, ctx, extension):
        await self.bot.unload_extension(f"cogs.{extension}")
        self.bot.logger.info(f"Unloaded cogs.{extension}")
        await ctx.reply(f"Unloaded {extension}")

    @commands.command()
    @commands.has_any_role("Admins", "Mission pooler")
    @checks.is_owner()
    async def reload(self, ctx, extension):
        if extension == "all":
            cogs = self.bot.cogs
            for cog in cogs:
                await self.bot.reload_extension(f"cogs.{cog.lower()}")
                self.bot.logger.info(f"Reloaded cogs.{cog}")
                await ctx.reply(f"Reloaded {cog}")
        else:
            await self.bot.reload_extension(f"cogs.{extension}")
            self.bot.logger.info(f"Reloaded cogs.{extension}")
            await ctx.reply(f"Reloaded {extension}")

    @commands.command(name="latestlogs", aliases=["logs", "log"])
    @commands.has_any_role("Admins", "Mission pooler")
    @checks.is_owner()
    async def latestlogs(self, ctx, numberOfLines:int=5):
        """
        Get the latest <numberOfLines> of log file 
        """
        if numberOfLines > 15:
            numberOfLines = 15
        if ctx.channel.id != self.bot_data.moderation_channel:
            await ctx.reply(f"Cette commande doit être effectuée dans le canal <#{self.bot_data.moderation_channel}>")
            return

        logfile = self.bot.logger.handlers[1].baseFilename
        message = f"Loaded : {logfile}"

        with open(logfile, 'r') as f:
            lines = f.read().splitlines()
            last_lines = lines[-numberOfLines:]
        message += "\n```\n"
        for line in last_lines:
            message += f"{line}\n"
        message += "\n```"

        await ctx.reply(message)


async def setup(bot):
    bot.logger.info("Loading 'owner'")
    await bot.add_cog(Owner(bot))
