import dbus
import dbus.service
import multiprocessing
import dbus.mainloop.glib

from gi.repository import GLib
from gi.repository import GObject

from .data_model import Host
from .service_model import HostServices

class UPSMonitorService(dbus.service.Object):
    def __init__(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus_name = dbus.service.BusName("org.gdramis.UPSMonitorService", dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, "/org/gdramis/UPSMonitorService")

    def run(self):
        self._ups_host_services = HostServices()
        self._loop = GLib.MainLoop()
        print("UPS Monitor Service started")
        self._loop.run()
        print("UPS Monitor Service stopped")

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
        print(host_dict)
        self._ups_host_services.update_host(Host(host_dict=host_dict))

    @dbus.service.method("org.gdramis.UPSMonitorService.DeleteHost", in_signature='i', out_signature='')
    def delete_host(self, id):
        self._ups_host_services.delete_host(id)

    @dbus.service.method("org.gdramis.UPSMonitorService.Quit", in_signature='', out_signature='')
    def quit(self):
        print("  shutting down")
        self._loop.quit()

class UPSMonitorClient(GObject.Object):
    __gtype_name__ = 'UPSMonitorClient'

    def __init__(self):
        bus = dbus.SessionBus()
        service = bus.get_object('org.gdramis.UPSMonitorService', "/org/gdramis/UPSMonitorService")
        self._get_all_hosts_dbus = service.get_dbus_method('get_all_hosts', 'org.gdramis.UPSMonitorService.GetAllHosts')
        self._get_host_dbus = service.get_dbus_method('get_host', 'org.gdramis.UPSMonitorService.GetHost')
        self._get_host_by_name_dbus = service.get_dbus_method('get_host_by_name', 'org.gdramis.UPSMonitorService.GetHostByName')
        self._save_host_dbus = service.get_dbus_method('save_host', 'org.gdramis.UPSMonitorService.SaveHost')
        self._update_host_dbus = service.get_dbus_method('update_host', 'org.gdramis.UPSMonitorService.UpdateHost')
        self._delete_host_dbus = service.get_dbus_method('delete_host', 'org.gdramis.UPSMonitorService.DeleteHost')
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

    def get_host(self, id):
        return self._list_to_object_host(self._dbus_to_python(self._get_host_dbus(id)))

    def get_host_by_name(self, name):
        return self._list_to_object_host(self._dbus_to_python(self._get_host_by_name_dbus(name)))

class UPSMonitorServiceStarter(GObject.Object):
    __gtype_name__ = 'UPSMonitorServiceStarter'

    @staticmethod
    def start_backend():
        UPSMonitorService().run()

    def start(self):
        multiprocessing.set_start_method('spawn')
        process = multiprocessing.Process(target = UPSMonitorServiceStarter.start_backend, daemon = True)
        process.start()
        return process
