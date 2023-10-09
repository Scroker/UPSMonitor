import dbus

class UPSMonitorClient():

    def __init__(self):
        bus = dbus.SessionBus()
        service = bus.get_object('org.gdramis.UPSMonitorService', "/org/gdramis/UPSMonitorService")
        self.get_all_hosts_dbus = service.get_dbus_method('get_all_hosts', 'org.gdramis.UPSMonitorService.GetAllHosts')
        self.quit_service_dbus = service.get_dbus_method('quit', 'org.gdramis.UPSMonitorService.Quit')

    def dbus_to_python(self, data):
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
            data = [self.dbus_to_python(value) for value in data]
        elif isinstance(data, dbus.Dictionary):
            new_data = dict()
            for key in data.keys():
                new_data[self.dbus_to_python(key)] = self.dbus_to_python(data[key])
            data = new_data
        return data

    def run(self):
        print ("Hosts:", self.dbus_to_python(self.get_all_hosts_dbus()))
