GDC Bot
========================================

Tools needed:
--------------

* python version 3.8.10 or lastest

Libraries
---------

* Creating a Bot: https://discordpy.readthedocs.io/en/latest/discord.html
* Discord.py (2.3.2):
  * Doc and site: https://discordpy.readthedocs.io/en/stable

* PyYaml (6.0):
  * Used to read config files

* Requests (2.31.0):
  * Used to get pbo files sent into the discord

* Systemd (0.17.1):
  * Used for logging. If your system does not support this package (MacOS, Windows...), remove it from the `requirement.txt` file.

Installation
------------

* Clone this repository
* Copy `config-sample.yml` into `config.yml`
* Edit `config.yml` as you need to.
* [Optional] Create a new virtual-env (I highly recommend to create one)
* Install requirement using python or python3 (depending on your environment)
```
python3 -m pip install -r requirements.txt
```
* [Optional] Copy `data-sample.yml` into `data.yml`
* Edit `data.yml` as you need. It must contain at least these keys : `messages` (must be a list), `announcement_channel`, `moderation_channel`. The `messages` list is just a list of fun messages that appear under the Bot name. The `announcement_channel` is the ID if the General channel, and the `moderation_channel` is the IS of the Officers channel. All this is optional and used ones can be defined later with bot command in `Owner` section. Default moderation channel will be the "System Messages Channel".

Starting
---------

    $ python3 bot.py
    $ # or if using venv
    $ .venv/bin/python3 bot.py

Bot should appear online if no error are raised

Development
-------------

VS Code is usefull with its debugging tools.

Heavily advised to have different Bot running prod and dev

Deployment
----------

Bot can be run automatically on Linux server.

Here is an example using systemd and venv on debian server (replace `username`, `groupname` & `/path/to/bot` according to your configuration)

```bash
[Unit]
Description=Start discord bot as service
After=multi-user.target

[Service]
Type=idle
User=username
Group=groupname
WorkingDirectory=/path/to/bot
ExecStart=/path/to/bot/.venv/bin/python3 /path/to/bot/bot.py
Restart=always
TimeoutStartSec=10
RestartSec=20

[Install]
WantedBy=multi-user.target
```

Credit
------

This project is issued from [GDC's bot](https://github.com/GdC-Framework/GDC_Bot)

Rewrited by [Basox70](https://github.com/basox70) in Python
