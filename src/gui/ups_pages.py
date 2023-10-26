from gi.repository import Adw, Gtk

from .data_model import UPS
from .ups_monitor_daemon import UPSMonitorClient, NotificationType

@Gtk.Template(resource_path='/org/ponderorg/UPSMonitor/ui/ups_preferences_page.ui')
class UpsPreferencesPage(Adw.NavigationPage):
    __gtype_name__ = 'UpsPreferencesPage'

    battery_row = Gtk.Template.Child()
    battery_image = Gtk.Template.Child()
    battery_level_bar = Gtk.Template.Child()
    voltage_label = Gtk.Template.Child()
    input_voltage_label = Gtk.Template.Child()
    output_voltage_label = Gtk.Template.Child()
    status_image = Gtk.Template.Child()
    status_label = Gtk.Template.Child()
    current_label = Gtk.Template.Child()
    frequency_label = Gtk.Template.Child()
    window_title = Gtk.Template.Child()
    informations_row = Gtk.Template.Child()
    settings_row = Gtk.Template.Child()
    notifications_row = Gtk.Template.Child()
    battery_voltage_label = Gtk.Template.Child()
    battery_low_voltage_label = Gtk.Template.Child()
    battery_high_voltage_label = Gtk.Template.Child()
    battery_nominal_voltage_label = Gtk.Template.Child()
    start_delay_label = Gtk.Template.Child()
    shutdown_delay_label = Gtk.Template.Child()
    nominal_voltage_label = Gtk.Template.Child()
    fault_voltage_label = Gtk.Template.Child()

    def __init__(self, **kwargs):
        self.ups_data = kwargs.get("ups_data", None)
        if self.ups_data != None:
            kwargs.pop("ups_data")
        super().__init__(**kwargs)
        self._dbus_client = UPSMonitorClient()
        self._dbus_signal_handler = self._dbus_client.connect_to_signal("ups_updated", self.update_self)
        self.connect("destroy", self.on_destroy)
        if self.ups_data.host_id == None:
            self.settings_row.set_visible(False)
            self.notifications_row.set_visible(False)
        self.update_self()

    def update_self(self):
        if self.ups_data != None and self.ups_data.host_id != None:
            ups_data = self._dbus_client.get_ups_by_name_and_host(self.ups_data.host_id, self.ups_data.key)
            if ups_data != None:
                self.ups_data = ups_data
        charge = int(self.ups_data.battery["charge"])
        if 'status' not in self.ups_data.ups.keys():
            image_name = "battery-action-symbolic"
        elif self.ups_data.ups["status"] == "OB":
            self.status_image.set_from_icon_name('error-symbolic')
            self.status_label.set_label('Offline')
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
            self.status_image.set_from_icon_name('check-round-outline-whole-symbolic')
            self.status_label.set_label('Online')
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
        self.battery_voltage_label.set_label(self.ups_data.battery['voltage'] + " V")
        self.battery_low_voltage_label.set_label(self.ups_data.battery['voltage.low'] + " V")
        self.battery_high_voltage_label.set_label(self.ups_data.battery['voltage.high'] + " V")
        self.battery_nominal_voltage_label.set_label(self.ups_data.battery['voltage.nominal'] + " V")
        self.battery_image.set_from_icon_name(image_name)
        self.battery_level_bar.set_value(charge)
        self.battery_row.set_subtitle(str(charge) + "%")
        self.voltage_label.set_label(self.ups_data.output['voltage'] + " V")
        self.input_voltage_label.set_label(self.ups_data.input['voltage'] + " V")
        self.nominal_voltage_label.set_label(self.ups_data.input['voltage.nominal'] + " V")
        self.fault_voltage_label.set_label(self.ups_data.input['voltage.fault'] + " V")
        self.output_voltage_label.set_label(self.ups_data.output['voltage'] + " V")
        self.current_label.set_label(self.ups_data.input['current.nominal'] + " A")
        self.window_title.set_title(self.ups_data.ups_name)
        self.window_title.set_title(self.ups_data.ups_name)
        self.start_delay_label.set_label(self.ups_data.ups['delay.start'] + " ms")
        self.shutdown_delay_label.set_label(self.ups_data.ups['delay.shutdown'] + " ms")
        self.frequency_label.set_label(self.ups_data.input['frequency.nominal'] + " Hz")

    def on_destroy(self, widget):
        self._dbus_signal_handler.remove()

@Gtk.Template(resource_path='/org/ponderorg/UPSMonitor/ui/ups_informations_page.ui')
class UpsInfoPage(Adw.NavigationPage):
    __gtype_name__ = 'UpsInfoPage'

    firmware_label = Gtk.Template.Child()
    window_title = Gtk.Template.Child()
    model_label = Gtk.Template.Child()
    productid_label = Gtk.Template.Child()
    vendorid_label = Gtk.Template.Child()
    type_label = Gtk.Template.Child()
    driver_version_usb_label = Gtk.Template.Child()
    driver_vesion_internal_label = Gtk.Template.Child()
    driver_name_label = Gtk.Template.Child()
    driver_version_label = Gtk.Template.Child()
    driver_port_label = Gtk.Template.Child()
    driver_syncronous_label = Gtk.Template.Child()
    driver_polling_interval_label = Gtk.Template.Child()

    def __init__(self, **kwargs):
        self.ups_data = kwargs.get("ups_data", None)
        if self.ups_data != None:
            kwargs.pop("ups_data")
        super().__init__(**kwargs)
        self._dbus_client = UPSMonitorClient()
        self.window_title.set_title(self.ups_data.ups_name)
        self.update_self()

    def update_self(self):
        if self.ups_data != None and self.ups_data.host_id != None:
            ups_data = self._dbus_client.get_ups_by_name_and_host(self.ups_data.host_id, self.ups_data.key)
            if ups_data != None:
                self.ups_data = ups_data
        # Device group
        if self.ups_data.ups['firmware'] != '':
            self.firmware_label.set_label(self.ups_data.ups['firmware'])
        if self.ups_data.ups['model'] != '':
            self.model_label.set_label(self.ups_data.ups['model'])
        if self.ups_data.ups['productid'] != '':
            self.productid_label.set_label(self.ups_data.ups['productid'])
        if self.ups_data.ups['vendorid'] != '':
            self.vendorid_label.set_label(self.ups_data.ups['vendorid'])
        if self.ups_data.ups['type'] != '':
            self.type_label.set_label(self.ups_data.ups['type'])
        # Driver group
        if self.ups_data.driver['name'] != '':
            self.driver_name_label.set_label(self.ups_data.driver['name'])
        if self.ups_data.driver['version'] != '':
            self.driver_version_label.set_label(self.ups_data.driver['version'])
        if self.ups_data.driver['version.internal'] != '':
            self.driver_vesion_internal_label.set_label(self.ups_data.driver['version.internal'])
        if self.ups_data.driver['version.usb'] != '':
            self.driver_version_usb_label.set_label(self.ups_data.driver['version.usb'])
        if self.ups_data.driver['parameter.pollinterval'] != '':
            self.driver_polling_interval_label.set_label(self.ups_data.driver['parameter.pollinterval'])
        if self.ups_data.driver['parameter.synchronous'] != '':
            self.driver_syncronous_label.set_label(self.ups_data.driver['parameter.synchronous'])
        if self.ups_data.driver['parameter.port'] != '':
            self.driver_port_label.set_label(self.ups_data.driver['parameter.port'])

@Gtk.Template(resource_path='/org/ponderorg/UPSMonitor/ui/ups_notifications_page.ui')
class UpsNotificationsPage(Adw.NavigationPage):
    __gtype_name__ = 'UpsNotificationsPage'

    window_title = Gtk.Template.Child()
    offline_notify_switch = Gtk.Template.Child()
    low_battery_notify_switch = Gtk.Template.Child()

    def __init__(self, **kwargs):
        self.ups_data = kwargs.get("ups_data", None)
        if self.ups_data != None:
            kwargs.pop("ups_data")
        super().__init__(**kwargs)
        self._dbus_client = UPSMonitorClient()
        self.window_title.set_title(self.ups_data.ups_name)
        self.notifications = self._dbus_client.get_all_ups_notifications(self.ups_data)
        if NotificationType.IS_OFFLINE in self.notifications:
            self.offline_notify_switch.set_active(True)
        else:
            self.offline_notify_switch.set_active(False)
        if NotificationType.LOW_BATTERY in self.notifications:
            self.low_battery_notify_switch.set_active(True)
        else:
            self.low_battery_notify_switch.set_active(False)

    @Gtk.Template.Callback()
    def offline_notify_switch_selected(self, widget, args):
        if self.offline_notify_switch.get_active() and NotificationType.IS_OFFLINE not in self.notifications:
            self._dbus_client.set_ups_notification_type(self.ups_data, NotificationType.IS_OFFLINE, True)
            self.notifications = self._dbus_client.get_all_ups_notifications(self.ups_data)
        elif not self.offline_notify_switch.get_active() and NotificationType.IS_OFFLINE in self.notifications:
            self._dbus_client.set_ups_notification_type(self.ups_data, NotificationType.IS_OFFLINE, False)
            self.notifications = self._dbus_client.get_all_ups_notifications(self.ups_data)

    @Gtk.Template.Callback()
    def low_battery_notify_switch_selected(self, widget, args):
        if self.low_battery_notify_switch.get_active() and NotificationType.LOW_BATTERY not in self.notifications:
            self._dbus_client.set_ups_notification_type(self.ups_data, NotificationType.LOW_BATTERY, True)
            self.notifications = self._dbus_client.get_all_ups_notifications(self.ups_data)
        elif not self.low_battery_notify_switch.get_active() and NotificationType.LOW_BATTERY in self.notifications:
            self._dbus_client.set_ups_notification_type(self.ups_data, NotificationType.LOW_BATTERY, False)
            self.notifications = self._dbus_client.get_all_ups_notifications(self.ups_data)


@Gtk.Template(resource_path='/org/ponderorg/UPSMonitor/ui/ups_settings_page.ui')
class UpsSettingsPage(Adw.NavigationPage):
    __gtype_name__ = 'UpsSettingsPage'

    window_title = Gtk.Template.Child()
    shutdown_low_battery_switch = Gtk.Template.Child()

    def __init__(self, **kwargs):
        self.ups_data = kwargs.get("ups_data", None)
        if self.ups_data != None:
            kwargs.pop("ups_data")
        super().__init__(**kwargs)
        self._dbus_client = UPSMonitorClient()
        self.window_title.set_title(self.ups_data.ups_name)
        self.notifications = self._dbus_client.get_all_ups_notifications(self.ups_data)
        if NotificationType.AUTO_SHUTDOWN in self.notifications:
            self.shutdown_low_battery_switch.set_active(True)
        else:
            self.shutdown_low_battery_switch.set_active(False)

    @Gtk.Template.Callback()
    def shutdown_low_battery_switch_selected(self, widget, args):
        if self.shutdown_low_battery_switch.get_active() and NotificationType.AUTO_SHUTDOWN not in self.notifications:
            self._dbus_client.set_ups_notification_type(self.ups_data, NotificationType.AUTO_SHUTDOWN, True)
            self.notifications = self._dbus_client.get_all_ups_notifications(self.ups_data)
        elif not self.shutdown_low_battery_switch.get_active() and NotificationType.AUTO_SHUTDOWN in self.notifications:
            self._dbus_client.set_ups_notification_type(self.ups_data, NotificationType.AUTO_SHUTDOWN, False)
            self.notifications = self._dbus_client.get_all_ups_notifications(self.ups_data)

@Gtk.Template(resource_path='/org/ponderorg/UPSMonitor/ui/home_page.ui')
class HomePage(Adw.NavigationPage):
    __gtype_name__ = 'HomePage'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
