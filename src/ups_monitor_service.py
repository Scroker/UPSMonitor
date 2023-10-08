import dbus
import dbus.service
import dbus.mainloop.glib

from gi.repository import GLib

class UPSMonitorService(dbus.service.Object):
   def __init__(self, message):
      self._message = message

   def run(self):
      dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
      bus_name = dbus.service.BusName("org.gdramis.UPSMonitorService", dbus.SessionBus())
      dbus.service.Object.__init__(self, bus_name, "/org/gdramis/UPSMonitorService")

      self._loop = GLib.MainLoop()
      print("Service running...")
      self._loop.run()
      print("Service stopped")

   @dbus.service.method("org.gdramis.UPSMonitorService.Message", in_signature='', out_signature='s')
   def get_message(self):
      print("  sending message")
      return self._message

   @dbus.service.method("org.gdramis.UPSMonitorService.Quit", in_signature='', out_signature='')
   def quit(self):
      print("  shutting down")
      self._loop.quit()
