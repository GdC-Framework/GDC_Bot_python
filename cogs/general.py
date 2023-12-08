import asyncio
import hashlib

from datetime import datetime
from time import time
from random import randint, getrandbits
from asyncio import sleep, TimeoutError

import discord
from discord.ext import commands
from discord.ext.commands import Context

from utils import checks, config, database

cfg = config.Config()
messages = config.Messages()
data = config.Data()


def is_admin(ctx):
    if int(ctx.author.id) in cfg.idOwner:
        return True
    for role in ctx.author.roles:
        if cfg.roleAdmin == role.id:
            return True
    return False


class General(commands.Cog, name="General"):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.msg_delay = 30
        self.msg_type_emoji = {"success": ":white_check_mark:",
                             "error": ":x:",
                             "info": ":information_source:",
                             "warning": ":warning:"}
        self.existing_roles = ["mission pooler",
                              "admins"]

    # region Fonctions utilisées par les commandes
    async def reply(self, ctx, msg_type: str, message: str, delete_after: int=30):
        """
        Répond à la commande avec un message
        """
        if delete_after:
            if msg_type in self.msg_type_emoji:
                await ctx.reply(f"{self.msg_type_emoji[msg_type]} {message}", delete_after=delete_after)
            else:
                await ctx.reply(f":grey_question: {message}", delete_after=delete_after)
            # si c'est une commande normale
            if ctx.clean_prefix != "/":
                # Attendre pendant `delete_after` secondes
                if ctx.guild:
                    await sleep(delete_after)
                    await ctx.message.delete()
        else:
            if msg_type in self.msg_type_emoji:
                await ctx.reply(f"{self.msg_type_emoji[msg_type]} {message}")
            else:
                await ctx.reply(f":grey_question: {message}")

    def get_user_role_level(self, user: discord.Member) -> int:
        """
        Retourne le niveau de rôle de l'utilisateur
        """
        user_role = 0
        for role in user.roles:
            if role.name.lower() == '@everyone':
                continue
            if role.name.lower() in self.existing_roles:
                user_role += 2**self.existing_roles.index(role.name.lower())
            else:
                user_role += len(self.existing_roles)
        return user_role

    async def get_user_guild_role_level(self, user: discord.Member) -> int:
        """
        Retourne le niveau de rôle de l'utilisateur dans le serveur
        """
        user_role = 0
        for guild in self.bot.guilds:
            if guild.id == cfg.idGuild:
                member = await guild.fetch_member(user.id)
                break
        for role in member.roles:
            if role.name.lower() == '@everyone':
                continue
            if role.name.lower() in self.existing_roles:
                user_role += 2**self.existing_roles.index(role.name.lower())
            else:
                user_role += len(self.existing_roles)
        return user_role

    # endregion

    # region Commandes

    @commands.command()
    async def ping(self, ctx):
        """
        Display ping of the bot
        """
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Le bot a une lantence de {round(self.bot.latency * 1000)}ms.",
            color=0x9C84EF
        )
        await ctx.reply(embed=embed)

    
    @commands.command()
    async def info(self, ctx):
        """
        Display some info about the bot
        """
        embed = discord.Embed(
            title=f"{self.bot.user.display_name}{f'#{self.bot.user.discriminator}' if int(self.bot.user.discriminator) > 0 else ''}",
            timestamp=datetime.now(),
            description=messages.bot_infos,
            color=discord.Color.blurple()
        )
        embed.set_author(name=self.bot.user.display_name,icon_url=self.bot.user.display_avatar.url)
        # embed.set_thumbnail(url=f"{self.bot.user.display_avatar.url}")
        await ctx.send(embed=embed)


    # le role @everyone est utile pour ne pas lancer cette commande en DM
    @commands.hybrid_command()
    @commands.has_any_role("@everyone")
    async def whoami(self, ctx:Context):
        """
        Display an ID card of the author
        """
        admin = is_admin(ctx)
        roles_name = [role.name for role in ctx.author.roles[1:]]

        embed = discord.Embed(title=f"{ctx.author.name}{f'#{ctx.author.discriminator}' if int(ctx.author.discriminator) > 0 else ''}", timestamp=datetime.now(), color=discord.Color.purple())
        embed.set_author(name=ctx.author.display_name,icon_url=ctx.author.display_avatar.url)
        embed.add_field(name="Compte créé le", value=f"{ctx.author.created_at.strftime('%d/%m/%Y %H:%M')}")
        embed.add_field(name="A rejoint le serveur le ", value=f"{ctx.author.joined_at.strftime('%d/%m/%Y %H:%M')}")
        embed.add_field(name="Rôles", value=", ".join(roles_name))
        if admin:
            embed.add_field(name="Est admin du bot",value="")
        embed.set_thumbnail(url=f"{ctx.author.display_avatar.url}")
        await ctx.send(embed=embed)



    @commands.hybrid_command()
    async def guess(self, ctx, number: int=10):
        """
        Devine un nombre entre 1 and <number>
        """
        await ctx.send(f"Devine un nombre entre 1 et {number}. Tu as 10 secondes.", delete_after=20)

        def is_correct(m):
            return m.author == ctx.author and m.content.isdigit()

        answer = randint(1, number)

        try:
            guess = await self.bot.wait_for('message', check=is_correct, timeout=10.0)
            if int(guess.content) == answer:
                await ctx.send("Tu as bon !", delete_after=10)
            else:
                await ctx.send(f"Oups. C'était {answer}.", delete_after=10)
        except TimeoutError:
            await ctx.send(f"Désolé, tu as mis trop de temps. La réponse était {answer}.", delete_after=10)

        # si c'est une commande normale
        await sleep(10)
        if ctx.guild:
            await guess.delete()
        if ctx.clean_prefix != "/":
            # Attendre pendant 10 secondes
            await ctx.message.delete()
    

    
    @commands.hybrid_command(name="lance", aliases=["roll", "r", "l"])
    async def lance(self, ctx, n: str="1", number: int=20):
        """
        Lance <n> dés <number> (limite à 100 dés et 100 faces)
        eg : r 2 6, r 2d6, lance 2 20
        """
        if "d" in n:
            n = n.split("d")
            try:
                number = int(n[1])
                n = int(n[0])
            except Exception:
                await ctx.reply(f"Un nombre est attendu à la place de {n}")
                return
        else:
            try:
                n = int(n)
            except Exception:
                await ctx.reply(f"Un nombre est attendu à la place de {n}")
                return
        if n > 100:
            n = 100
        if number > 100:
            number = 100
        
        if n < 1:
            await ctx.reply("Tu ne peux pas lancer moins d'un dé")
            return
        if number < 4:
            await ctx.reply("Tu ne peux pas lancer un dé à moins de 4 faces")
            return
        if number % 2 != 0:
            await ctx.reply("Tu ne peux pas lancer un dé impair")
            return

        answer = [randint(1, number) for _ in range(0,n)]

        color = min(answer) == 1 and 0xff0000 or (max(answer) == number and 0x00ff00 or 0x777777)

        embed = discord.Embed(
            title=f"Lance {str(n)}d{str(number)}",
            description=f"Resultat : {[n for n in answer]} (Total : {sum(answer)})",
            color=color
        )
        await ctx.reply(embed=embed)
    


    @commands.hybrid_command(name="flip", aliases=["f", "coin", "piece"])
    async def flip(self, ctx, n: int=1):
        """
        Lance une pièce <n>[max : 1000] fois
        eg : flip, flip 2
        """
        
        if n > 1000:
            n = 1000
        
        if n < 1:
            await ctx.reply("Tu ne peux pas lancer moins d'une pièce")
            return
        
        result = ["pile", "face"]

        answer = [result[randint(0, 1)] for _ in range(0,n)]

        embed = discord.Embed(
            title=f"Flip {str(n) if n > 1 else ''}",
            description=f"""__Resultat__ : {", ".join(answer) if n <= 50 else ''}
            {f"**Total** : {answer.count('pile')} pile(s) et {answer.count('face')} face(s)" if n > 1 else ''}""",
            color=0xC4AE1E
        )
        await ctx.reply(embed=embed)



    @commands.hybrid_command(name="deletedms", aliases=["del","suppr"])
    async def delete_dms(self, ctx):
        """
        Supprime les messages privés non epinglés
        """
        if ctx.guild:
            await ctx.reply("Cette commande ne peut être utilisée que dans les DMs", delete_after=10)
            await sleep(10)
            await ctx.message.delete()
            return

        new_message = await ctx.reply('En cours !')
        
        msg_history_list = [message async for message in ctx.channel.history(limit=1000)]
        msg_history_list = ctx.clean_prefix == "/" and msg_history_list[1:] or msg_history_list[2:]
        msg_pinned = await ctx.channel.pins()
        for msg in msg_history_list:
            if msg.author.bot and msg not in msg_pinned:
                await msg.delete()
                await sleep(1)

        await new_message.delete()
        self.bot.logger.info(f"Suppression de {len(msg_history_list)} message(s) dans les DMs de {ctx.author.display_name}")
    


    #endregion


async def setup(bot):
    bot.logger.info("Loading 'general'")
    await bot.add_cog(General(bot))