import dbus, logging
import dbus.service
import multiprocessing
import dbus.mainloop.glib

from gi.repository import Gio, GLib, GObject
from pynut3.nut3 import PyNUT3Error

from .data_model import Host, UPS, NotificationType
from .service_model import HostServices, UPServices

class ConversionUtil(GObject.Object):
    __gtype_name__ = 'ConversionUtil'


    @staticmethod
    def object_to_string(host:Host) -> dict:
        host_dict = vars(host)
        return ConversionUtil.python_to_string(host_dict)

    @staticmethod
    def python_to_string(host_dict:dict) -> dict:
        if host_dict['host_id'] == None:
            host_dict['host_id'] = 'None'
        if host_dict['username'] == None:
            host_dict['username'] = 'None'
        if host_dict['profile_name'] == None:
            host_dict['profile_name'] ='None'
        if (host_dict['password'] == None):
            host_dict['password'] = 'None'
        return host_dict

    @staticmethod
    def string_to_python(host_dict:dict) -> dict:
        if host_dict['host_id'] == 'None':
            host_dict['host_id'] = None
        if host_dict['username'] == 'None':
            host_dict['username'] = None
        if host_dict['profile_name'] == 'None':
            host_dict['profile_name'] = None
        if (host_dict['password'] == 'None'):
            host_dict['password'] = None
        return host_dict

    @staticmethod
    def dbus_to_python(data):
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
            data = [ConversionUtil.dbus_to_python(value) for value in data]
        elif isinstance(data, dbus.Dictionary):
            new_data = {}
            for key in data.keys():
                new_data[ConversionUtil.dbus_to_python(key)] = ConversionUtil.dbus_to_python(data[key])
            data = new_data
        return data

    @staticmethod
    def python_to_dbus(data):
        if isinstance(data, str):
            data = dbus.String(data)
        elif isinstance(data, bool):
            data = dbus.Boolean(data)
        elif isinstance(data, int):
            data = dbus.Int64(data)
        elif isinstance(data, float):
            data = dbus.Double(data)
        elif isinstance(data, list):
            data = dbus.Array([ConversionUtil.python_to_dbus(value) for value in data], signature='v')
        elif isinstance(data, dict):
            data = dbus.Dictionary(data, signature='sv')
            for key in data.keys():
                data[key] = ConversionUtil.python_to_dbus(data[key])
        return data

    @staticmethod
    def list_to_object_host(host_dict:dict) -> Host:
        if 'host_id' in host_dict.keys():
            return Host(host_dict=host_dict)
        else:
            return None

    @staticmethod
    def transform_ups_dict(ups_dict:dict) -> UPS:
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
        return ups


class UPSMonitorService(dbus.service.Object):

    _connected_flag = False
    _offline_ups_notified = []
    _low_battery_ups_notified = []
    _ups_saved_host_connections = []
    _ups_retry_host_connections = []
    _temporary_host_list = []
    _ups_data = []
    _ups_connected_number = 0
    _service_name = 'org.gdramis.UPSMonitorService'
    _object_path = '/org/gdramis/UPSMonitorService'

    def __init__(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        session_bus = dbus.SessionBus()
        self._setting = Gio.Settings.new('org.ponderorg.UPSMonitor')
        self._setting.connect('changed', self.on_settings_property_change)
        bus_name = dbus.service.BusName('org.gdramis.UPSMonitorService')
        dbus.service.Object.__init__(self, bus_name, '/org/gdramis/UPSMonitorService')

        # Freedesktop Portals
        portal_service = session_bus.get_object('org.freedesktop.portal.Desktop', '/org/freedesktop/portal/desktop')
        self._add_notification = portal_service.get_dbus_method('AddNotification', 'org.freedesktop.portal.Notification')
        self._request_background = portal_service.get_dbus_method('RequestBackground', 'org.freedesktop.portal.Background')
        self._ups_host_services = HostServices()
        self._ups_retry_host_connections = self._ups_host_services.get_all_hosts()

    def on_settings_property_change(self, widget, args):
        if self._setting.get_value("run-at-boot"):
            self._request_background('org.gdramis.UPSMonitorService', {'background':True, 'autostart':True, 'commandline':['upsmonitor','-b']})
        if self._setting.get_value("run-in-background") and not self._setting.get_value("run-at-boot"):
            self._request_background('org.gdramis.UPSMonitorService', {'background':True, 'autostart':False})
        if not self._setting.get_value("run-in-background"):
            self._request_background('org.gdramis.UPSMonitorService', {'background':False, 'autostart':False, 'commandline':['upsmonitor','-b']})

    def _check_routine(self):
        self._start_connection()
        self._update_all_ups()
        if self._ups_connected_number != len(self._ups_data):
            self._ups_connected_number = len(self._ups_data)
            self.ups_changed()
        self.ups_updated()
        for ups_dict in self._ups_data:
            notification_types = self._ups_host_services.get_all_ups_notifications(ups_dict['host_id'], ups_dict['name'])
            if ups_dict['ups.status'] != 'OL' and ups_dict['name'] not in self._offline_ups_notified and 2 in notification_types :
                self._offline_ups_notified.append(ups_dict['name'])
                message = 'Charge at ' + ups_dict['battery.charge'] + '%'
                self._add_notification('org.gdramis.UPSMonitorService', {'icon':'battery-caution-symbolic','title':ups_dict['name.pretty'], 'body': message, 'priority':'urgent'})
            if ups_dict['ups.status'] != 'OL' and int(ups_dict['battery.charge']) <= 20 and ups_dict['name'] not in self._low_battery_ups_notified and 1 in notification_types :
                self._offline_ups_notified.append(ups_dict['name'])
                message = 'Charge at ' + ups_dict['battery.charge'] + '%'
                self._add_notification('org.gdramis.UPSMonitorService', {'icon':'battery-empty-symbolic','title':ups_dict['name.pretty'], 'body': message, 'priority':'urgent'})
        return True

    def _start_connection(self):
        connected_host = []
        for host_dict in self._ups_retry_host_connections:
            try:
                ups_services = UPServices(host_dict)
                self._ups_saved_host_connections.append(ups_services)
                connected_host.append(host_dict)
            except PyNUT3Error as e:
                logging.exception("UPS Monitor Service: error during connection with host " + host_dict['ip_address'])
        for host_dict in connected_host:
            self._ups_retry_host_connections.remove(host_dict)
        self.connection_initialized()

    def _update_all_ups(self):
        self._ups_data = []
        for connection in self._ups_saved_host_connections:
            try:
                self._ups_data += connection.get_all_hosts_ups()
            except PyNUT3Error as e:
                logging.exception("UPS Monitor Service: error during connection with host " + host_dict['ip_address'])
                self._ups_saved_host_connections.remove(connection)
                host_dict = self._ups_host_services.get_host(connection.host['host_id'])
                self._ups_retry_host_connections.append(host_dict)

    def run(self):
        GObject.timeout_add_seconds(5, self._check_routine)
        self._loop = GLib.MainLoop()
        logging.info("UPS Monitor Service: started")
        self._loop.run()
        logging.info("UPS Monitor Service: stopped")

    # Service method and signals

    @dbus.service.signal("org.gdramis.UPSMonitorService")
    def connection_initialized(self):
        logging.info("UPS Monitor Service: connection initialized")

    @dbus.service.method("org.gdramis.UPSMonitorService", in_signature='', out_signature='')
    def quit(self):
        print("  shutting down")
        self._loop.quit()

    # Host method and signals

    @dbus.service.signal("org.gdramis.UPSMonitorService.Host")
    def host_updated(self):
        logging.info("UPS Monitor Service: host updated")

    @dbus.service.signal("org.gdramis.UPSMonitorService.Host")
    def host_deleated(self):
        logging.info("UPS Monitor Service: host deleated")

    @dbus.service.method("org.gdramis.UPSMonitorService.Host", in_signature='', out_signature='aa{sv}')
    def get_all_temporary_hosts(self):
        host_list = []
        for host in self._temporary_host_list:
            host_list.append(ConversionUtil.python_to_string(host))
        return host_list

    @dbus.service.method("org.gdramis.UPSMonitorService.Host", in_signature='', out_signature='aa{sv}')
    def get_all_hosts(self):
        hosts = []
        for host in self._ups_host_services.get_all_hosts():
            host_dict = ConversionUtil.python_to_string(host)
            hosts.append(host_dict)
        return hosts

    @dbus.service.method("org.gdramis.UPSMonitorService.Host", in_signature='i', out_signature='a{sv}')
    def get_host(self, id):
        host_dict = {}
        host = self._ups_host_services.get_host(id)
        if host != None:
            host_dict = ConversionUtil.python_to_string(host)
        return host_dict

    @dbus.service.method("org.gdramis.UPSMonitorService.Host", in_signature='s', out_signature='a{sv}')
    def get_host_by_name(self, name):
        host_dict = {}
        host = self._ups_host_services.get_host_by_name(name)
        if host != None:
            host_dict = ConversionUtil.python_to_string(host)
        return host_dict

    @dbus.service.method("org.gdramis.UPSMonitorService.Host", in_signature='a{sv}', out_signature='')
    def save_host(self, host_dict:dict):
        host_dict = ConversionUtil.string_to_python(ConversionUtil.dbus_to_python(host_dict))
        self._ups_host_services.save_host(host_dict)
        self._ups_retry_host_connections.append(host_dict)
        self.host_updated()

    @dbus.service.method("org.gdramis.UPSMonitorService.Host", in_signature='a{sv}', out_signature='')
    def update_host(self, host_dict:dict):
        host_dict = ConversionUtil.string_to_python(ConversionUtil.dbus_to_python(host_dict))
        connection_to_remove = None
        host_to_remove = None
        for connection in self._ups_saved_host_connections:
            if connection.host['host_id'] == host_dict['host_id']:
                connection_to_remove = connection
        for host_dict_retry in self._ups_retry_host_connections:
            if host_dict_retry['host_id'] == host_dict['host_id']:
                host_to_remove = host_dict_retry
        if connection_to_remove != None :
            self._ups_saved_host_connections.remove(connection_to_remove)
        if host_to_remove != None :
            self._ups_retry_host_connections.remove(host_to_remove)
        self._ups_host_services.update_host(host_dict)
        self._ups_retry_host_connections.append(host_dict)
        self.host_updated()

    @dbus.service.method("org.gdramis.UPSMonitorService.Host", in_signature='i', out_signature='')
    def delete_host(self, host_id):
        self._ups_host_services.delete_host(host_id)
        connection_to_remove = None
        host_to_remove = None
        for connection in self._ups_saved_host_connections:
            if connection.host['host_id'] == host_id:
                connection_to_remove = connection
        for host_dict_retry in self._ups_retry_host_connections:
            if host_dict_retry['host_id'] == host_id:
                host_to_remove = host_dict_retry
        if connection_to_remove != None :
            self._ups_saved_host_connections.remove(connection_to_remove)
        if host_to_remove != None :
            self._ups_retry_host_connections.remove(host_to_remove)
        self.host_deleated()

    @dbus.service.method("org.gdramis.UPSMonitorService.Host", in_signature='a{sv}', out_signature='b')
    def host_connection(self, host_dict:dict):
        host_dict = ConversionUtil.string_to_python(ConversionUtil.dbus_to_python(host_dict))
        try:
            ups_services = UPServices(host_dict)
            if host_dict['profile_name'] != None:
                self._ups_saved_host_connections.append(ups_services)
            else:
                self._temporary_host_list.append(host_dict)
                self._ups_saved_host_connections.append(ups_services)
            self.connection_initialized()
            return True
        except PyNUT3Error as error:
            logging.exception("UPS Monitor Service: error during connection with host ", host_dict['ip_address'])
            return False

    # UPS method and signals

    @dbus.service.signal("org.gdramis.UPSMonitorService.UPS")
    def ups_changed(self):
        logging.info("UPS Monitor Service: ups changed")

    @dbus.service.signal("org.gdramis.UPSMonitorService.UPS")
    def ups_updated(self):
        logging.info("UPS Monitor Service: ups updated")

    @dbus.service.method("org.gdramis.UPSMonitorService.UPS", in_signature='', out_signature='aa{sv}')
    def get_all_ups(self):
        return self._ups_data

    @dbus.service.method("org.gdramis.UPSMonitorService.UPS", in_signature='a{sv}', out_signature='')
    def set_ups_notification_type(self, notify_dict:dict):
        self._ups_host_services.set_ups_notification_type(notify_dict['host_id'], notify_dict['name'], notify_dict['type'], notify_dict['active'])

    @dbus.service.method("org.gdramis.UPSMonitorService.UPS", in_signature='a{sv}', out_signature='ai')
    def get_all_ups_notifications(self, notify_dict:dict):
        result = self._ups_host_services.get_all_ups_notifications(notify_dict['host_id'], notify_dict['name'])
        return result

    @dbus.service.method("org.gdramis.UPSMonitorService.UPS", in_signature='is', out_signature='a{sv}')
    def get_ups_by_name_and_host(self, host_id:int, ups_name:str):
        for ups_dict in self._ups_data:
            if ups_dict['name'] == ups_name and ups_dict['host_id'] == host_id:
                return ups_dict
        return {}

class UPSMonitorClient(GObject.Object):
    __gtype_name__ = 'UPSMonitorClient'

    def __init__(self):
        bus = dbus.SessionBus(mainloop=dbus.mainloop.glib.DBusGMainLoop(set_as_default=True))
        self._service = bus.get_object('org.gdramis.UPSMonitorService', "/org/gdramis/UPSMonitorService")
        self._introspect_dbus = self._service.get_dbus_method('Introspect', 'org.freedesktop.DBus.Introspectable')
        self._quit_service_dbus = self._service.get_dbus_method('quit', 'org.gdramis.UPSMonitorService')

        self._get_all_ups_dbus = self._service.get_dbus_method('get_all_ups', 'org.gdramis.UPSMonitorService.UPS')
        self._set_ups_notification_type = self._service.get_dbus_method('set_ups_notification_type', 'org.gdramis.UPSMonitorService.UPS')
        self._get_all_ups_notifications = self._service.get_dbus_method('get_all_ups_notifications', 'org.gdramis.UPSMonitorService.UPS')
        self._get_ups_by_name_and_host = self._service.get_dbus_method('get_ups_by_name_and_host', 'org.gdramis.UPSMonitorService.UPS')

        self._get_all_hosts_dbus = self._service.get_dbus_method('get_all_hosts', 'org.gdramis.UPSMonitorService.Host')
        self._get_all_temporary_hosts_dbus = self._service.get_dbus_method('get_all_temporary_hosts', 'org.gdramis.UPSMonitorService.Host')
        self._get_host_dbus = self._service.get_dbus_method('get_host', 'org.gdramis.UPSMonitorService.Host')
        self._get_host_by_name_dbus = self._service.get_dbus_method('get_host_by_name', 'org.gdramis.UPSMonitorService.Host')
        self._save_host_dbus = self._service.get_dbus_method('save_host', 'org.gdramis.UPSMonitorService.Host')
        self._update_host_dbus = self._service.get_dbus_method('update_host', 'org.gdramis.UPSMonitorService.Host')
        self._delete_host_dbus = self._service.get_dbus_method('delete_host', 'org.gdramis.UPSMonitorService.Host')
        self._host_connection_dbus = self._service.get_dbus_method('host_connection', 'org.gdramis.UPSMonitorService.Host')

    def connect_to_signal(self, signal_name, callback_func):
        return self._service.connect_to_signal(signal_name, callback_func)

    def introspect(self):
        return self._introspect_dbus()

    def get_all_ups(self):
        UPSs = []
        for ups_dict in ConversionUtil.dbus_to_python(self._get_all_ups_dbus()):
            ups = ConversionUtil.transform_ups_dict(ups_dict)
            UPSs.append(ups)
        return UPSs

    def get_all_hosts(self):
        hosts = []
        for host_dict in ConversionUtil.dbus_to_python(self._get_all_hosts_dbus()):
            hosts.append(Host(host_dict=host_dict))
        return hosts

    def get_all_temporary_hosts(self):
        hosts = []
        for host_dict in ConversionUtil.dbus_to_python(self._get_all_temporary_hosts_dbus()):
            hosts.append(Host(host_dict=host_dict))
        return hosts

    def get_ups_by_name_and_host(self, host_id:int, ups_name:str):
        ups_dict = self._get_ups_by_name_and_host(host_id,ups_name)
        if len(ups_dict) > 0 :
            return ConversionUtil.transform_ups_dict(ups_dict)
        else:
            return None

    def set_ups_notification_type(self, ups:UPS, notification_type:NotificationType, enabled:bool):
        notify_dict = {}
        notify_dict['host_id'] = ups.host_id
        notify_dict['name'] = ups.key
        notify_dict['type'] = int(notification_type)
        notify_dict['active'] = enabled
        self._set_ups_notification_type(ConversionUtil.python_to_dbus(notify_dict))

    def get_all_ups_notifications(self, ups:UPS):
        notify_dict = {}
        notify_dict['host_id'] = ups.host_id
        notify_dict['name'] = ups.key
        return self._get_all_ups_notifications(ConversionUtil.python_to_dbus(notify_dict))

    def save_host(self, host:Host):
        host_dict = ConversionUtil.object_to_string(host)
        self._save_host_dbus(host_dict)

    def update_host(self, host:Host):
        host_dict = ConversionUtil.object_to_string(host)
        self._update_host_dbus(host_dict)

    def delete_host(self, host_id:int):
        self._delete_host_dbus(host_id)

    def host_connection(self, host:Host):
        host_dict = ConversionUtil.object_to_string(host)
        return self._host_connection_dbus(host_dict)

    def get_host(self, id):
        return ConversionUtil.list_to_object_host(ConversionUtil.dbus_to_python(self._get_host_dbus(id)))

    def get_host_by_name(self, host_name):
        return ConversionUtil.list_to_object_host(ConversionUtil.dbus_to_python(self._get_host_by_name_dbus(host_name)))

    def quit_service_dbus(self):
        self._quit_service_dbus()

class UPSMonitorServiceStarter(GObject.Object):
    __gtype_name__ = 'UPSMonitorServiceStarter'

    def __init__(self):
        self.process = None

    @staticmethod
    def start_backend():
        UPSMonitorService().run()

    def start(self):
        multiprocessing.set_start_method('spawn')
        logging.info("Starting ups services")
        try:
            UPSMonitorClient()
        except dbus.exceptions.DBusException as e:
            if e._dbus_error_name == 'org.freedesktop.DBus.Error.ServiceUnknown':
                self.process = multiprocessing.Process(target = UPSMonitorServiceStarter.start_backend, daemon = True)
                self.process.start()

    def join(self):
        if self.process != None:
            self.process.join()
