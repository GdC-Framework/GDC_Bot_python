LSD-Bot : le Bot des Scorpions du Désert
========================================

Tools needed:
--------------

* python version 3.8.10 or lastest

Libraries
---------

* Creating a Bot: https://discordpy.readthedocs.io/en/latest/discord.html
* Discord.py (2.3.2):
  * Doc and site: https://discordpy.readthedocs.io/en/stable
* Mariadb (1.1.6):
  * Used to connect to mysql/maria database
  * Might need of installing mariadb lastest client library following next steps: 
    * Needed for MariaDB Connector/C, which is a requirement for this python library:
      ```bash
      sudo apt-key adv --recv-keys --keyserver keyserver.ubuntu.com 0xcbcb082a1bb943db
      curl -LsS https://downloads.mariadb.com/MariaDB/mariadb_repo_setup | sudo bash
      sudo apt-get update && sudo apt-get upgrade && sudo apt-get dist-upgrade
      sudo apt-get install libmariadb3 libmariadb-dev
      ```

* PyYaml (6.0):
  * Used to read config files
  
* PsUtil (5.9.5):
  * Used to launch only 1 instance of the bot, whatever launch method you use

* Systemd (0.17.1):
  * Used for logging. If your system does not support this package (MacOS...), remove it from the `requirement.txt` file.

Database
--------

Mariadb can be use, initiated by all script available [here](https://github.com/YannZeRookie/lsd-account/tree/master/db) run in order

It is possible to run the bot without database

Installation
------------

* Clone this repository
* Copy `config-sample.yml` into `config.yml`
* Edit `config.yml` as you need to. Note that there are two features that change the roles of users on a regular basis, so you want to turn them off in a pre-production context. See the `#Critical` options
* [Optional] Create a new virtual-env 
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

VS Code is usefull with its debuggin tools.

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

This project is issued from [YannZeRookie's bot](https://github.com/YannZeRookie/lsd-bot)

Rewrited and modernized by [Basox70](https://github.com/basox70) in Python
