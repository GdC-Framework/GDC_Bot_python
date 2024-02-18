""" Read configuration file
"""
import sys
from pathlib import Path
from typing import TypedDict

import yaml

# pylint: disable=W0621
# Contain all Class to load config, data and messages

config_file = Path("config.yml")
data_file = Path("data.yml")
messages_file = Path("messages.yml")


class Config(object):
    """Bot config object
    """
    def __init__(self, file_path: str | Path) -> None:

        # Just some linter definitions, does nothing
        self.connection_url: Path
        self.bot_name: str
        self.token: str
        self.prefix: str
        self.role_admin: list
        self.gmail_user: str
        self.gmail_password: str
        self.id_owner: list[int]
        self.id_guild: int
        self.logger: LoggerConfig





        with open(file_path, encoding="utf-8") as file:
            config = yaml.safe_load(file)
            for k in config:
                self.__setattr__(k, config[k])

    def build_login_url(self, key: str | Path) -> Path:
        return self.connection_url / key

class LoggerConfig(TypedDict):
    """Some linter definitions again, just a classic dict with known keys
    """
    debug_level: str
    max_bytes: int
    backup_count: int

class Data(object):
    def __init__(self):
        with open(data_file) as file:
            data = yaml.load(file, yaml.Loader)
            for k in data.__dict__:
                setattr(self, k, getattr(data, k))

    def save(self, data):
        with open(data_file, "w") as f:
            yaml.dump(data, f, indent=2)
            return True
        return False


class Messages(object):
    def __init__(self):
        with open(messages_file, encoding="utf-8") as file:
            messages = yaml.safe_load(file)
            for k in messages:
                setattr(self, k, messages[k])



bot_configuration = Config(Path("config.yml"))
