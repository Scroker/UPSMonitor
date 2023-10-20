import sqlite3, os
from pynut3 import nut3
from gi.repository import GObject
from .data_model import UPS, Host

class HostNameAlreadyExist(Exception):

    def __init__(self):
        super().__init__()

class HostAddressAlreadyExist(Exception):

    def __init__(self):
        super().__init__()

class UPServices(GObject.Object):
    ___gtype_name__ = 'UPServices'

    def __init__(self, host:dict):
        super().__init__()
        self.host = host
        if host['username'] != None and host['password'] != None:
            self.client = nut3.PyNUT3Client(host=host['ip_address'], login=host['username'], password=host['password'], port=host['port'])
        else:
            self.client = nut3.PyNUT3Client(host=host['ip_address'], port=host['port'])

    def get_all_hosts_ups(self):
        ups_list = []
        ups_dict = self.client.get_dict_ups()
        for k1, v1 in ups_dict.items():
            vars_dict = self.client.get_dict_vars(k1)
            identifier = { "name" : k1 , "name.pretty" : v1 }
            if isinstance(self.host['host_id'], int):
                identifier['host_id'] = self.host['host_id']
            else:
                identifier['host_id'] = 'None'
            vars_dict.update(identifier)
            ups_list.append(vars_dict)
        return ups_list

class HostServices(GObject.Object):
    __gtype_name__ = 'HostServices'

    def __init__(self):
        super().__init__()
        self.conn = sqlite3.connect('.var/app/org.ponderorg.UPSMonitor/data/ups_monitor.db')
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS hosts
                             (id             INTEGER    PRIMARY KEY     AUTOINCREMENT,
                              profile_name   CHAR(50),
                              ip_address     TEXT       NOT NULL,
                              port           INTEGER    NOT NULL,
                              username       CHAR(50),
                              password       CHAR(50));''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS notifications
                             (id            INTEGER     PRIMARY KEY     AUTOINCREMENT,
                              name          CHAR(50),
                              host_id       INTEGER     NOT NULL,
                              type          INTEGER     NOT NULL);''')
        self.conn.commit()

    def get_all_hosts(self) -> []:
        cursor = self.conn.cursor()
        result = cursor.execute("SELECT id, profile_name, ip_address, port, username, password FROM hosts")
        host_list = []
        for row in result:
            host_list.append({'ip_address':row[2], 'port':row[3], 'profile_name':row[1], 'host_id':row[0], 'username':row[3], 'password':row[4]})
        return host_list

    def get_host(self, host_id:int) -> []:
        cursor = self.conn.cursor()
        result = cursor.execute("SELECT id, profile_name, ip_address, port, username, password FROM hosts WHERE id=?", (host_id,))
        for row in result:
           return {'ip_address':row[2], 'port':row[3], 'profile_name':row[1], 'host_id':row[0], 'username':row[3], 'password':row[4]}
        return None

    def get_host_by_name(self, host_name:str) -> []:
        cursor = self.conn.cursor()
        result = cursor.execute("SELECT id, profile_name, ip_address, port, username, password FROM hosts WHERE profile_name=?", (host_name,))
        for row in result:
           return {'ip_address':row[2], 'port':row[3], 'profile_name':row[1], 'host_id':row[0], 'username':row[3], 'password':row[4]}
        return None

    def set_ups_notification_type(self, host_id:int, ups_name:str, notification_type:int, active:bool = True) -> []:
        cursor = self.conn.cursor()
        notification_types = {}
        cursor.execute("SELECT * FROM hosts WHERE id=?", (host_id,))
        if cursor.fetchone() is not None:
            cursor.execute("SELECT * FROM notifications WHERE name=? AND host_id=? AND type=?", (ups_name, host_id, int(notification_type)))
            if active and cursor.fetchone() is None:
                result = cursor.execute("INSERT INTO notifications (name, host_id, type) VALUES (?,?,?)", (ups_name, host_id, int(notification_type)))
            elif not active :
                result = cursor.execute("DELETE FROM notifications WHERE name=? AND host_id=? AND type=?", (ups_name, host_id, int(notification_type)))
            self.conn.commit()
        else:
            pass

    def get_all_ups_notifications(self, host_id:int, ups_name:str) -> []:
        cursor = self.conn.cursor()
        notification_types = []
        result = cursor.execute("SELECT type FROM notifications WHERE name=? AND host_id=?", (ups_name, host_id,))
        for notification_type in result:
            notification_types.append(notification_type[0])
        return notification_types

    def save_host(self, host:dict):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM hosts WHERE profile_name=?", (host['profile_name'],))
        if cursor.fetchone() is not None:
            raise HostNameAlreadyExist
        cursor.execute("SELECT * FROM hosts WHERE ip_address=?", (host['ip_address'],))
        if cursor.fetchone() is not None:
            raise HostAddressAlreadyExist
        if host['username'] != None or host['username'] != None:
            cursor.execute("INSERT INTO hosts (profile_name, ip_address, port,username, password) VALUES (?,?,?,?,?)", (host['profile_name'], host['ip_address'], host['port'], host['username'], host['password']))
        else:
            cursor.execute("INSERT INTO hosts (profile_name, ip_address, port) VALUES (?,?,?)", (host['profile_name'], host['ip_address'], host['port']))
        self.conn.commit()

    def update_host(self, host:dict):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE hosts SET ip_address=?, port=?, profile_name=?, username=?, password=? WHERE id=?", (host['ip_address'], host['port'], host['profile_name'], host['username'], host['password'], host['host_id']))
        self.conn.commit()

    def delete_host(self, host_id:int):
        self.conn.execute("DELETE FROM hosts WHERE id=?", (host_id,))
        self.conn.execute("DELETE FROM notifications WHERE host_id=?", (host_id,))
        self.conn.commit()

