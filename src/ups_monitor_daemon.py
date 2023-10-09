import dbus
import dbus.service
import multiprocessing
import dbus.mainloop.glib

from gi.repository import GLib
from gi.repository import GObject
from pynut3.nut3 import PyNUT3Error

from .data_model import Host, UPS
from .service_model import HostServices, UPServices

class UPSMonitorService(dbus.service.Object):
    def __init__(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        session_bus = dbus.SessionBus()
        bus_name = dbus.service.BusName("org.gdramis.UPSMonitorService", session_bus)
        dbus.service.Object.__init__(self, bus_name, "/org/gdramis/UPSMonitorService")
        notification_service = session_bus.get_object('org.freedesktop.Notifications', "/org/freedesktop/Notifications")
        self._notify = notification_service.get_dbus_method('Notify', 'org.freedesktop.Notifications')
        self._ups_host_services = HostServices()
        self._offline_ups_notified = []
        self._low_battery_ups_notified = []

    def hello(self):
        try:
            for host_dict in self.get_all_ups():
                if host_dict['ups.status'] != 'OL' and host_dict['name'] not in self._offline_ups_notified :
                    self._offline_ups_notified.append(host_dict['name'])
                    self._notify("", 0, "battery-caution-symbolic", host_dict['name.pretty'] + " is now offline!", "Charge at " + host_dict['battery.charge'] + "%", [], {"urgency": 1}, 3000)
                if host_dict['ups.status'] != 'OL' and int(host_dict['battery.charge']) <= 20 and host_dict['name'] not in self._low_battery_ups_notified :
                    self._offline_ups_notified.append(host_dict['name'])
                    self._notify("", 0, "battery-empty-symbolic", host_dict['name.pretty'] + " have low battery!", "Charge at " + host_dict['battery.charge'] + "%", [], {"urgency": 1}, 3000)
        except PyNUT3Error as e:
            print("Error, try reset connections!")
            self._start_connection()
        return True

    def _start_connection(self):
        self._ups_host_connections = []
        for host in self._ups_host_services.get_all_hosts():
            try:
                ups_services = UPServices(host)
                self._ups_host_connections.append(ups_services)
            except PyNUT3Error as e:
                pass

    def run(self):
        self._start_connection()
        GObject.timeout_add_seconds(5, self.hello)
        self._loop = GLib.MainLoop()
        print("UPS Monitor Service started")
        self._loop.run()
        print("UPS Monitor Service stopped")

    @dbus.service.method("org.gdramis.UPSMonitorService.GetAllUPS", in_signature='', out_signature='aa{sv}')
    def get_all_ups(self):
        UPSs = []
        for connection in self._ups_host_connections:
            UPSs += connection.get_all_hosts_ups()
        return UPSs

    @dbus.service.method("org.gdramis.UPSMonitorService.GetAllHosts", in_signature='', out_signature='aa{sv}')
    def get_all_hosts(self):
        hosts = []
        for host in self._ups_host_services.get_all_hosts():
            host_dict = vars(host)
            if (host_dict['username'] == None):
                host_dict['username'] = 'None'
            if (host_dict['password'] == None):
                host_dict['password'] = 'None'
            hosts.append(host_dict)
        return hosts

    @dbus.service.method("org.gdramis.UPSMonitorService.GetHost", in_signature='i', out_signature='a{sv}')
    def get_host(self, id):
        host_dict = {}
        host = self._ups_host_services.get_host(id)
        if host != None:
            host_dict = vars(host)
            if (host_dict['username'] == None):
                host_dict['username'] = 'None'
            if (host_dict['password'] == None):
                host_dict['password'] = 'None'
        return host_dict

    @dbus.service.method("org.gdramis.UPSMonitorService.GetHostByName", in_signature='s', out_signature='a{sv}')
    def get_host_by_name(self, name):
        host_dict = {}
        host = self._ups_host_services.get_host_by_name(name)
        if host != None:
            host_dict = vars(host)
            if (host_dict['username'] == None):
                host_dict['username'] = 'None'
            if (host_dict['password'] == None):
                host_dict['password'] = 'None'
        return host_dict

    @dbus.service.method("org.gdramis.UPSMonitorService.SaveHost", in_signature='a{sv}', out_signature='')
    def save_host(self, host_dict:dict):
        if (host_dict['host_id'] == 'None'):
            host_dict['host_id'] = None
        if (host_dict['username'] == 'None'):
            host_dict['username'] = None
        if (host_dict['password'] == 'None'):
            host_dict['password'] = None
        self._ups_host_services.save_host(Host(host_dict=host_dict))


    @dbus.service.method("org.gdramis.UPSMonitorService.UpdateHost", in_signature='a{sv}', out_signature='')
    def update_host(self, host_dict:dict):
        if (host_dict['username'] == 'None'):
            host_dict['username'] = None
        if (host_dict['password'] == 'None'):
            host_dict['password'] = None
        self._ups_host_services.update_host(Host(host_dict=host_dict))

    @dbus.service.method("org.gdramis.UPSMonitorService.DeleteHost", in_signature='i', out_signature='')
    def delete_host(self, id):
        self._ups_host_services.delete_host(id)

    @dbus.service.method("org.gdramis.UPSMonitorService.Quit", in_signature='', out_signature='')
    def quit(self):
        print("  shutting down")
        self._loop.quit()

    @dbus.service.method("org.gdramis.UPSMonitorService.HostConnection", in_signature='a{sv}', out_signature='b')
    def host_connection(self, host_dict:dict):
        try:
            ups_services = UPServices(Host(host_dict=host_dict))
            self.ups_host_connections.append(ups_services)
            return True
        except PyNUT3Error as error:
            print("Error during connection with Host: ", error.args[0])
            return False

class UPSMonitorClient(GObject.Object):
    __gtype_name__ = 'UPSMonitorClient'

    def __init__(self):
        bus = dbus.SessionBus()
        service = bus.get_object('org.gdramis.UPSMonitorService', "/org/gdramis/UPSMonitorService")
        self._introspect_dbus = service.get_dbus_method('Introspect', 'org.freedesktop.DBus.Introspectable')
        self._get_all_ups_dbus = service.get_dbus_method('get_all_ups', 'org.gdramis.UPSMonitorService.GetAllUPS')
        self._get_all_hosts_dbus = service.get_dbus_method('get_all_hosts', 'org.gdramis.UPSMonitorService.GetAllHosts')
        self._get_host_dbus = service.get_dbus_method('get_host', 'org.gdramis.UPSMonitorService.GetHost')
        self._get_host_by_name_dbus = service.get_dbus_method('get_host_by_name', 'org.gdramis.UPSMonitorService.GetHostByName')
        self._save_host_dbus = service.get_dbus_method('save_host', 'org.gdramis.UPSMonitorService.SaveHost')
        self._update_host_dbus = service.get_dbus_method('update_host', 'org.gdramis.UPSMonitorService.UpdateHost')
        self._delete_host_dbus = service.get_dbus_method('delete_host', 'org.gdramis.UPSMonitorService.DeleteHost')
        self._host_connection_dbus = service.get_dbus_method('host_connection', 'org.gdramis.UPSMonitorService.HostConnection')
        self._quit_service_dbus = service.get_dbus_method('quit', 'org.gdramis.UPSMonitorService.Quit')

    def _dbus_to_python(self, data):
        if isinstance(data, dbus.String):
            if str(data) == 'None':
                data = None
            else:
                data = str(data)
        elif isinstance(data, dbus.Boolean):
            data = bool(data)
        elif isinstance(data, dbus.Int64) or isinstance(data, dbus.Int32):
            data = int(data)
        elif isinstance(data, dbus.Double):
            data = float(data)
        elif isinstance(data, dbus.Array):
            data = [self._dbus_to_python(value) for value in data]
        elif isinstance(data, dbus.Dictionary):
            new_data = dict()
            for key in data.keys():
                new_data[self._dbus_to_python(key)] = self._dbus_to_python(data[key])
            data = new_data
        return data

    def _list_to_object_host(self, host_dict:dict):
        if 'host_id' in host_dict.keys():
            return Host(host_dict=host_dict)
        else:
            return None
    def introspect(self):
        return self._introspect_dbus()

    def get_all_ups(self):
        UPSs = []
        for ups_dict in self._dbus_to_python(self._get_all_ups_dbus()):
            ups = UPS(ups_dict["name"] , ups_dict["name.pretty"], ups_dict["host_id"])
            for k2, v2 in ups_dict.items():
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
            UPSs.append(ups)
        return UPSs

    def get_all_hosts(self):
        hosts = []
        for host_dict in self._dbus_to_python(self._get_all_hosts_dbus()):
            hosts.append(Host(host_dict=host_dict))
        return hosts

    def save_host(self, host:Host):
        host_dict = vars(host)
        if host_dict['host_id'] == None:
            host_dict['host_id'] = 'None'
        if host_dict['username'] == None:
            host_dict['username'] = 'None'
        if (host_dict['password'] == None):
            host_dict['password'] = 'None'
        self._save_host_dbus(host_dict)

    def update_host(self, host:Host):
        host_dict = vars(host)
        if host_dict['username'] == None:
            host_dict['username'] = 'None'
        if (host_dict['password'] == None):
            host_dict['password'] = 'None'
        self._update_host_dbus(host_dict)

    def delete_host(self, host_id:int):
        self._delete_host_dbus(host_id)

    def host_connection(self, host:Host):
        host_dict = vars(host)
        if host_dict['host_id'] == None:
            host_dict['host_id'] = 'None'
        if host_dict['username'] == None:
            host_dict['username'] = 'None'
        if host_dict['profile_name'] == None:
            host_dict['profile_name'] = 'None'
        if (host_dict['password'] == None):
            host_dict['password'] = 'None'
        self._host_connection_dbus(host_dict)

    def get_host(self, id):
        return self._list_to_object_host(self._dbus_to_python(self._get_host_dbus(id)))

    def get_host_by_name(self, name):
        return self._list_to_object_host(self._dbus_to_python(self._get_host_by_name_dbus(name)))

class UPSMonitorServiceStarter(GObject.Object):
    __gtype_name__ = 'UPSMonitorServiceStarter'

    def __init__(self):
        self.process = None

    @staticmethod
    def start_backend():
        UPSMonitorService().run()

    def start(self):
        multiprocessing.set_start_method('spawn')
        try:
            UPSMonitorClient()
        except dbus.exceptions.DBusException as e:
            if e._dbus_error_name == 'org.freedesktop.DBus.Error.ServiceUnknown':
                self.process = multiprocessing.Process(target = UPSMonitorServiceStarter.start_backend, daemon = True)
                self.process.start()

    def join(self):
        if self.process != None:
            self.process.join()
