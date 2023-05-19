import sqlite3

from pynut3 import nut3

from gi.repository import GObject
from .data_model import UPS, Host

class UPServices(GObject.Object):
    ___gtype_name__ = 'UPServices'

    def __init__(self, host:Host):
        super().__init__()
        if host.username != None and host.password != None:
            self.client = nut3.PyNUT3Client(host=host.ip_address, login=host.username, password=host.password, port=host.port)
        else:
            self.client = nut3.PyNUT3Client(host=host.ip_address, port=host.port)

    def get_all_ups(self):
        ups_dict = self.client.get_dict_ups()
        ups_list = []
        for k1, v1 in ups_dict.items():
            ups = UPS(k1 , v1)
            vars_dict = self.client.get_dict_vars(k1)
            for k2, v2 in vars_dict.items():
                if "battery." in k2:
                    ups.battery[k2.replace('battery.','')]=v2
                elif "device." in k2:
                    ups.device[k2.replace('device.','')]=v2
                elif "driver." in k2:
                    k2.replace('driver.','')
                    ups.driver[k2.replace('driver.','')]=v2
                elif "input." in k2:
                    k2.replace('input.','')
                    ups.input[k2.replace('input.','')]=v2
                elif "output." in k2:
                    k2.replace('output.','')
                    ups.output[k2.replace('output.','')]=v2
                elif "ups." in k2:
                    ups.ups[k2.replace('ups.','')]=v2
            ups_list.append(ups)
        return ups_list

class HostServices(GObject.Object):
    __gtype_name__ = 'HostServices'

    def __init__(self):
        super().__init__()
        self.conn = sqlite3.connect('ups_monitor.db')
        #self.conn.execute('''DROP TABLE IF EXISTS hosts''')
        self.conn.execute('''CREATE TABLE IF NOT EXISTS hosts
                             (id             INTEGER     PRIMARY KEY    AUTOINCREMENT,
                             ip_address      TEXT         NOT NULL,
                             port            INTEGER     NOT NULL,
                             username        CHAR(50),
                             password        REAL);''')

    def get_all_hosts(self) -> []:
        query = "SELECT id, ip_address, port, username, password FROM HOSTS"
        cursor = self.conn.execute(query)
        host_list = []
        for row in cursor:
           host_list.append(Host(row[1], row[2], row[0], row[3], row[4]))
        return host_list

    def get_host(self, host_id:int) -> []:
        query = "SELECT id, ip_address, port, username, password FROM hosts WHERE id=" + str(host_id)
        cursor = self.conn.execute(query)
        for row in cursor:
           return Host(row[1], row[2], row[0], row[3], row[4])
        return host_list

    def save_host(self, host:Host):
        if host.username != None or host.username != None:
            query = "INSERT INTO hosts (ip_address,port,username, password) VALUES ('" + host.ip_address + "'," + str(host.port) + "," + host.username + "," + host.password + ")"
        else:
            query = "INSERT INTO hosts (ip_address,port) VALUES ('" + host.ip_address + "'," + str(host.port) + ")"
        self.conn.execute(query)
        self.conn.commit()

    def update_host(self, host:Host):
        query = "UPDATE hosts SET ip_address='" + host.ip_address + "', port=" + ste(host.port )+ ", username='" + host.username + "', password='" + host.password + "' WHERE ID=" + str(host.host_id) + ")"
        self.conn.execute(query)
        self.conn.commit()

    def delete_host(self, host_id:int):
        query = "DELETE FROM hosts WHERE id=" + str(host_id)
        self.conn.execute(query)
        self.conn.commit()
