from gi.repository import Adw, Gtk
from .ups_monitor_daemon import UPSMonitorClient, NotificationType

@Gtk.Template(resource_path='/org/ponderorg/UPSMonitor/ui/ups_preferences_page.ui')
class UpsPreferencesPage(Adw.PreferencesPage):
    __gtype_name__ = 'UpsPreferencesPage'

    bettery_group = Gtk.Template.Child()
    device_group = Gtk.Template.Child()
    driver_group = Gtk.Template.Child()
    input_group = Gtk.Template.Child()
    output_group = Gtk.Template.Child()
    ups_group = Gtk.Template.Child()
    low_battery_notify_switch = Gtk.Template.Child()
    offline_notify_switch = Gtk.Template.Child()

    def __init__(self, **kwargs):
        self.ups_data = kwargs.get("ups_data", None)
        if self.ups_data != None:
            kwargs.pop("ups_data")
        super().__init__(**kwargs)
        self._dbus_client = UPSMonitorClient()
        notifications = self._dbus_client.get_all_ups_notifications(self.ups_data)
        if int(NotificationType.LOW_BATTERY) in notifications:
            self.low_battery_notify_switch.set_active(True)
        if int(NotificationType.IS_OFFLINE) in notifications:
            self.offline_notify_switch.set_active(True)
        self.update_self()

    def update_self(self):
        if self.ups_data != None:
            self.set_title(self.ups_data.ups_name)
            for k2 in self.ups_data.battery:
                v2 = self.ups_data.battery[k2]
                action_row = Adw.ActionRow()
                action_row.set_title(_(k2))
                if "charge" in k2:
                    action_row.set_subtitle(v2+"%")
                    progress = Gtk.ProgressBar(fraction=int(v2)/100)
                    progress.set_margin_top(20)
                    action_row.add_suffix(progress)
                else:
                    action_row.add_suffix(Gtk.Label(label=v2))
                self.bettery_group.add(action_row)
            for k2 in self.ups_data.device:
                v2 = self.ups_data.device[k2]
                action_row = self.create_action_row(k2,v2)
                self.device_group.add(action_row)
            for k2 in self.ups_data.driver:
                v2 = self.ups_data.driver[k2]
                action_row = self.create_action_row(k2,v2)
                self.driver_group.add(action_row)
            for k2 in self.ups_data.input:
                v2 = self.ups_data.input[k2]
                action_row = self.create_action_row(k2,v2)
                self.input_group.add(action_row)
            for k2 in self.ups_data.output:
                v2 = self.ups_data.output[k2]
                action_row = self.create_action_row(k2,v2)
                self.output_group.add(action_row)
            for k2 in self.ups_data.ups:
                v2 = self.ups_data.ups[k2]
                action_row = self.create_action_row(k2,v2)
                self.ups_group.add(action_row)

    def create_action_row(self, title:str, value:str):
        action_row = Adw.ActionRow()
        action_row.set_title(_(title))
        action_row.add_suffix(Gtk.Label(label=value))
        return action_row

    @Gtk.Template.Callback()
    def low_battery_notify_switch_selected(self, widget, args):
        if self.low_battery_notify_switch.get_active():
            self._dbus_client.set_ups_notification_type(self.ups_data, NotificationType.LOW_BATTERY, True)
        elif not self.low_battery_notify_switch.get_active():
            self._dbus_client.set_ups_notification_type(self.ups_data, NotificationType.LOW_BATTERY, False)

    @Gtk.Template.Callback()
    def offline_notify_switch_selected(self, widget, args):
        if self.offline_notify_switch.get_active():
            self._dbus_client.set_ups_notification_type(self.ups_data, NotificationType.IS_OFFLINE, True)
        elif not self.offline_notify_switch.get_active():
            self._dbus_client.set_ups_notification_type(self.ups_data, NotificationType.IS_OFFLINE, False)

    #@Gtk.Template.Callback()
    def shutdown_low_battery_switch_selected(self, widget, args):
        print("Implement shutdown service")
        return
