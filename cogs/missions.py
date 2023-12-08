import os, requests, shutil

from datetime import datetime
from time import time
from asyncio import sleep, TimeoutError

import discord
from discord.ext import commands
from discord.ext.commands import Context

from utils import checks, config, database

cfg = config.Config()
messages = config.Messages()
data = config.Data()

class Mission(commands.Cog, name="Mission"):
    def __init__(self, bot):
        self.bot = bot
        self.msg_delay = 30
        self.msg_type_emoji = {"success": ":white_check_mark:",
                             "error": ":x:",
                             "info": ":information_source:",
                             "warning": ":warning:"}
        self.existing_roles = ["mission pooler",
                              "admins"]
        self.react_emojis = ["❓", "✅", "❌"]
        self.days_in_month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    # region Fonctions utilisées par les commandes

    def is_leap_year(self, year):
        """Determine whether a year is a leap year."""

        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    def is_valid_date(self, dateToFormat) -> [int, int, str]:
        """
        Décompose la date `dateToFormat` en jour et mois, retourne l'erreur s'il y en a une
        """
        if "/" in dateToFormat:
            day, month = dateToFormat.split("/")
            
            # Trying to convert month into int and check if month is valid
            try:
                month = int(month)
            except Exception as e:
                return None, None, f"Le mois n'est pas valide `{month}`. Un nombre est attendu.\nErreur : {e}"
            if 1 < month > 12:
                return None, None, f"Le mois n'est pas valide `{month}`. Attendu entre 1 et 12"
            
            # Trying to convert day into int and check if day is valid for the previous month 
            try:
                day = int(day)
            except Exception as e:
                return None, None, f"Le jour n'est pas valide `{day}`. Un nombre est attendu.\nErreur : {e}"
            
            # If month is February
            if month == 2:
                # Year of the date : if month is earlier than current month, then consider it's the next year
                currYear = month < datetime.now().month and datetime.now().year + 1 or datetime.now().year
                if self.is_leap_year(currYear):
                    self.days_in_month[2] = 29
                else:
                    self.days_in_month[2] = 28
            
            if 1 < int(day) > self.days_in_month[month]:
                return None, None, f"Le jour n'est pas valide `{day}`. Attendu entre 1 et {self.days_in_month[month]} pour ce mois"
            
            return day, month, None
        else:
            return None, None, f"Je ne comprends pas la date `{dateToFormat}`"
        
    async def send_date(self, ctx, date:str) -> None:
        message = await ctx.send(f"{date}")
        for reaction in self.react_emojis:
            await message.add_reaction(reaction)

    # endregion

    # region Commandes

    @commands.command(name="next")
    @commands.has_any_role("Admins", "Mission pooler")
    @checks.is_owner()
    async def next(self, ctx, dateBegin=None, dateEnd=None):
        """
        !next [DD/MM] [DD/MM]

        Propose des dates avec réactions, allant de la première date à la deuxième, maximum de 14 jours

        1ere date: Si non spécifié prend le lendemain
        2ème date: Si non spécifié propose 7 jours suivant la première date
        """
        # checking if date are valid
        bDay = bMonth = eDay = eMonth = 0
        if dateBegin:
            bDay, bMonth, error = self.is_valid_date(dateBegin)
            if error:
                await ctx.reply(error)
                return
        else:
            bDay, bMonth = datetime.now().day + 1 , datetime.now().month
            
        if dateEnd:
            eDay, eMonth, error = self.is_valid_date(dateEnd)
            if error:
                await ctx.reply(error)
                return
        else:
            eDay = bDay + 6
            if eDay > self.days_in_month[bMonth]:
                eDay -= self.days_in_month[bMonth]
                eMonth = bMonth + 1 < 13 and bMonth + 1 or 1
            else:
                eMonth = bMonth
        
        # Create list of date
        dateList =[]
        if bMonth == eMonth:
            dateList = [f"{x:02}/{bMonth:02}" for x in range(bDay, eDay+1)]
        else:
            dateList = [f"{x:02}/{bMonth:02}" for x in range(bDay, self.days_in_month[bMonth]+1)]
            dateList += [f"{x:02}/{eMonth:02}" for x in range(1, eDay+1)]

        # limit to 14 entry max
        if dateList.__len__() > 14:
            dateList = dateList[:14]

        for eventDate in dateList:
            await self.send_date(ctx, eventDate)
        
        # await ctx.reply(f"{dateBegin}, {dateEnd}")

    @commands.command(name="mission")
    @commands.has_any_role("Admins", "Mission pooler")
    @checks.is_owner()
    async def mission(self, ctx):

        def download_file(url, filepath):
            with requests.get(url, stream=True) as r:
                with open(filepath, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)

        if ctx.message.attachments.__len__() == 0:
            await ctx.reply(f"Fichier *.pbo requis")
            return
        missionFile = ctx.message.attachments[0]

        if missionFile.filename[-3:] != 'pbo':
            await ctx.reply(f"Fichier non supporté : {missionFile.filename}. Fichier *.pbo requis")
            return
        url = missionFile.url
        filename = "pbo/" + missionFile.filename
        download_file(url, filename)

        ctx
        ...

    #endregion


async def setup(bot):
    bot.logger.info("Loading 'mission'")
    await bot.add_cog(Mission(bot))