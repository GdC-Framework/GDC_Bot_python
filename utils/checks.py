""""
Copyright © Krypton 2021 - https://github.com/kkrypt0nn (https://krypt0n.co.uk)
Description:
This is a template to create your own discord bot in python.

Version: 4.0.1
"""

import json

from discord.ext import commands
import logging
from utils import config
import exceptions

cfg = config.Config()



def is_owner():
    async def predicate(context: commands.Context) -> bool:        
        invoked_with = context.__dict__.get("invoked_with", None)
        logging.debug(f'=== is_owner ===invoked_with {invoked_with}')

        if context.author.id not in cfg.idOwner and invoked_with != "help":
            raise UserNotOwner
        return True

    return commands.check(predicate)


def not_blacklisted():
    async def predicate(context: commands.Context) -> bool:
        with open("blacklist.json") as file:
            data = json.load(file)
        if context.author.id in data["ids"]:
            raise UserBlacklisted
        return True

    return commands.check(predicate)
