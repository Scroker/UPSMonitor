import dbus
import dbus.service
import multiprocessing
import dbus.mainloop.glib

from gi.repository import GLib
from gi.repository import GObject
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
        dict_employee = vars(host)
        if (dict_employee['username'] == None):
            dict_employee['username'] = 'None'
        if (dict_employee['password'] == None):
            dict_employee['password'] = 'None'
        hosts.append(dict_employee)
      return hosts

   @dbus.service.method("org.gdramis.UPSMonitorService.Quit", in_signature='', out_signature='')
   def quit(self):
      print("  shutting down")
      self._loop.quit()

def start_backend():
    UPSMonitorService().run()

class UPSMonitorServiceStarter(GObject.Object):
    __gtype_name__ = 'UPSMonitorServiceStarter'

    def start(self):
        multiprocessing.set_start_method('spawn')
        process = multiprocessing.Process(target = start_backend, daemon = True)
        process.start()
