import dbus
import dbus.service
import dbus.mainloop.glib

from gi.repository import GLib
from .service_model import HostServices

class UPSMonitorService(dbus.service.Object):
   def __init__(self):
      pass

   def run(self):
      dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
      bus_name = dbus.service.BusName("org.gdramis.UPSMonitorService", dbus.SessionBus())
      dbus.service.Object.__init__(self, bus_name, "/org/gdramis/UPSMonitorService")

      self.ups_host_services = HostServices()

      self._loop = GLib.MainLoop()
      print("UPS Monitor Service started")
      self._loop.run()
      print("UPS Monitor Service stopped")

   @dbus.service.method("org.gdramis.UPSMonitorService.Message", in_signature='', out_signature='as')
   def get_message(self):
      host_names = []
      for host in self.ups_host_services.get_all_hosts():
        host_names.append(host.ip_address)
      return host_names

   @dbus.service.method("org.gdramis.UPSMonitorService.Quit", in_signature='', out_signature='')
   def quit(self):
      print("  shutting down")
      self._loop.quit()
