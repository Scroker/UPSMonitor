import sqlite3

from gi.repository import GObject

class Host(GObject.Object):
    __gtype_name__ = 'Host'

    def __init__(self, ip_address:str, port:int, username:str, password:str):
        super().__init__()
        self.ip_address = ip_address
        self.port = port
        self.username = username
        self.password = password

class NUTHost(Host):
    __gtype_name__ = 'NUTHost'
