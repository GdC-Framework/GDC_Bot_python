import os, sys, yaml

# Contain all Class to load config, data and messages

config_file = "config.yml"
data_file = "data.yml"
messages_file = "messages.yml"

class Config(object):
    def __init__(self):
        if not os.path.isfile(config_file):
            sys.exit(f"{config_file} not found! Please add it and try again.")
        else:
            with open(config_file) as file:
                config = yaml.safe_load(file)
                for k in config:
                    setattr(self, k, config[k])

    def build_login_url(self, key):
        return self.connection_url + '/' + key


class Data(object):
    def __init__(self):

        if not os.path.isfile(data_file):
            return
        else:
            with open(data_file) as file:
                data = yaml.load(file, yaml.Loader)
                for k in data.__dict__:
                    setattr(self, k, getattr(data,k))

    def save(self, data):
        with open(data_file, "w") as f:
            yaml.dump(data, f, indent=2)
            return True
        return False


class Messages(object):
    def __init__(self):
        if not os.path.isfile(messages_file):
            sys.exit(f"{messages_file} not found! Please add it and try again.")
        else:
            with open(messages_file, encoding='utf-8') as file:
                messages = yaml.safe_load(file)
                for k in messages:
                    setattr(self, k, messages[k])