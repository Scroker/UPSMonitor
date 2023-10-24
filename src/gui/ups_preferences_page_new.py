from gi.repository import Adw, Gtk

from .data_model import UPS
from .ups_monitor_daemon import UPSMonitorClient, NotificationType

@Gtk.Template(resource_path='/org/ponderorg/UPSMonitor/ui/ups_preferences_page_new.ui')
class UpsPreferencesPage(Adw.PreferencesPage):
    __gtype_name__ = 'UpsPreferencesPage'

    battery_row = Gtk.Template.Child()
    battery_image = Gtk.Template.Child()
    battery_level_bar = Gtk.Template.Child()
    voltage_label = Gtk.Template.Child()
    input_voltage_label = Gtk.Template.Child()
    output_voltage_label = Gtk.Template.Child()
    host_image = Gtk.Template.Child()
    host_label = Gtk.Template.Child()
    current_label = Gtk.Template.Child()
    frequency_label = Gtk.Template.Child()

    def __init__(self, **kwargs):
        ups_data = kwargs.get("ups_data", None)
        if ups_data != None:
            kwargs.pop("ups_data")
        super().__init__(**kwargs)
        self._dbus_client = UPSMonitorClient()
        self._dbus_signal_handler = self._dbus_client.connect_to_signal("ups_updated", self.update_self)
        self.connect("destroy", self.on_destroy)
        self.update_start(ups_data)

    def update_self(self, ups_data:UPS=None):
        if ups_data != None:
            self.ups_data = ups_data
        elif ups_data == None  and self.ups_data.host_id != None:
            self.ups_data = self._dbus_client.get_ups_by_name_and_host(self.ups_data.host_id, self.ups_data.key)
        else:
            return
        self.update_battery_row()

    def update_start(self, ups_data:UPS=None):
        if ups_data != None:
            self.ups_data = ups_data
        elif ups_data == None  and self.ups_data.host_id != None:
            self.ups_data = self._dbus_client.get_ups_by_name_and_host(self.ups_data.host_id, self.ups_data.key)
        else:
            return
        self.update_battery_row()

    def update_battery_row(self):
        charge = int(self.ups_data.battery["charge"])
        if 'status' not in self.ups_data.ups.keys():
            image_name = "battery-action-symbolic"
        elif self.ups_data.ups["status"] == "OB":
            if charge >= 90:
                image_name = "battery-full-symbolic"
            elif charge >= 80:
                image_name = "battery-level-90-symbolic"
            elif charge >= 70:
                image_name = "battery-level-70-symbolic"
            elif charge >= 60:
                image_name = "battery-level-60-symbolic"
            elif charge >= 50:
                image_name = "battery-level-50-symbolic"
            elif charge >= 40:
                image_name = "battery-level-40-symbolic"
            elif charge >= 30:
                image_name = "battery-level-30-symbolic"
            elif charge >= 20:
                image_name = "battery-level-20-symbolic"
            elif charge >= 10:
                image_name = "battery-leve-10-symbolic"
            else:
                image_name = "battery-level-0-symbolic"
        elif self.ups_data.ups["status"] == "OL":
            if charge >= 90:
                image_name = "battery-full-charging-symbolic"
            elif charge >= 80:
                image_name = "battery-level-90-charging-symbolic"
            elif charge >= 70:
                image_name = "battery-level-70-charging-symbolic"
            elif charge >= 60:
                image_name = "battery-level-60-charging-symbolic"
            elif charge >= 50:
                image_name = "battery-level-50-charging-symbolic"
            elif charge >= 40:
                image_name = "battery-level-40-charging-symbolic"
            elif charge >= 30:
                image_name = "battery-level-30-charging-symbolic"
            elif charge >= 20:
                image_name = "battery-level-20-charging-symbolic"
            elif charge >= 10:
                image_name = "battery-level-10-charging-symbolic"
            else:
                image_name = "battery-level-0-charging-symbolic"
        self.battery_image.set_from_icon_name(image_name)
        self.battery_level_bar.set_value(charge)
        self.battery_row.set_subtitle(str(charge) + " %")
        self.voltage_label.set_label(self.ups_data.output['voltage'] + " V")
        self.input_voltage_label.set_label(self.ups_data.input['voltage'] + " V")
        self.output_voltage_label.set_label(self.ups_data.input['voltage'] + " V")
        self.current_label.set_label(self.ups_data.input['current.nominal'] + " A")
        self.host_image.set_from_icon_name('preferences-desktop-remote-desktop-symbolic')
        self.frequency_label.set_label(self.ups_data.input['frequency.nominal'] + " Hz")
        host = self._dbus_client.get_host(self.ups_data.host_id)
        if self.ups_data.host_id != None:
            self.host_label.set_label(host.profile_name)
        else:
            self.host_label.set_label("N/A")

    def on_destroy(self, widget):
        self._dbus_signal_handler.remove()
