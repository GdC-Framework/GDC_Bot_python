import sys
try:
    from mariadb import connect, Error
except ImportError as e:
    connect = Error = None
from time import time


class Database(object):
    """docstring for Database"""
    def __init__(self, config):
        self.db_info = {"user": config.db_user,
                        "password": config.db_pass,
                        "host": config.db_host,
                        "port": config.db_port,
                        "database": config.db_name,
                        "connect_timeout": config.connect_timeout
                        }

        self.last_ok_check = 0
        self.cur = None
        self.conn = None
        self.isConnected = False

    def connect(self):
        try:
            db = connect(**self.db_info)
            self.last_ok_check = int(time())
        except Error as e:
            return False, ["Error", f"Error connecting to MariaDB Platform: {e}"]

        db.auto_reconnect = False
        self.cur = db.cursor(dictionary=True)
        self.conn = db
        self.isConnected = True
        return True, ["Success", "Connected to MariaDB Platform!"]

    def reconnect(self):
        try:
            self.conn.reconnect()
            self.last_ok_check = int(time())
            return True, ["Success", "Reconnected to MariaDB Platform!"]
        except Exception:
            return self.connect()
    
    def disconnect(self):
        try:
            self.conn.close()
        except Error as e:
            return False, ["Error", f"Error disconnecting to MariaDB Platform: {e}"]
        except Exception as e:
            return False, ["Error", f"Error disconnecting to MariaDB Platform: {e}"]
        self.isConnected = False
