import sqlite3

from gi.repository import GObject
from .data_model import NUTHost, Host

class HostServices(GObject.Object):
    __gtype_name__ = 'HostServices'

    def __init__(self):
        super().__init__()
        self.conn = sqlite3.connect('ups_monitor.db')
        #self.conn.execute('''DROP TABLE IF EXISTS HOSTS''')
        self.conn.execute('''CREATE TABLE IF NOT EXISTS HOSTS
                             (ID             INTEGER     PRIMARY KEY    AUTOINCREMENT,
                             IP_ADDRESS      TEXT         NOT NULL,
                             PORT            INTEGER     NOT NULL,
                             USERNAME        CHAR(50),
                             PASWORD         REAL);''')

    def get_hosts(self) -> []:
        cursor = self.conn.execute("SELECT id, ip_address, port from HOSTS")
        host_list = []
        for row in cursor:
           host_list.append(Host(row[1], row[2], None, None))
        return host_list

    def add_host(self, host:Host):
        query = "INSERT INTO HOSTS (IP_ADDRESS,PORT) VALUES ('" + str(host.ip_address) + "'," + str(host.port) + ")"
        self.conn.execute(query)
        self.conn.commit()

