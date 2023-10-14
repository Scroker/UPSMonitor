import threading
import dbus
import time

from gi.repository import Adw, Gtk, Gio, GObject

from .data_model import Host
from .add_new_server_box import AddNewServerBox
from .ups_monitor_daemon import UPSMonitorClient
from .host_preferences_page import HostPreferencesPage

@Gtk.Template(resource_path='/org/ponderorg/UPSMonitor/ui/monitor_preferences_window.ui')
class MonitorPreferencesWindow(Adw.PreferencesWindow):
    __gtype_name__ = 'MonitorPreferencesWindow'

    saved_profiles_list = Gtk.Template.Child()
    connect_button = Gtk.Template.Child()
    saved_profiles_group = Gtk.Template.Child()
    run_in_background = Gtk.Template.Child()
    temporary_profiles_list = Gtk.Template.Child()
    temporary_profiles_group = Gtk.Template.Child()
    first_connect_button = Gtk.Template.Child()
    no_host_connection = Gtk.Template.Child()
    no_dbus_connection = Gtk.Template.Child()
    dbus_client = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_server_box = AddNewServerBox()
        self.add_server_box.set_transient_for(self)
        self.add_server_box.set_modal(True)
        self.connect_button.connect("clicked", self.on_add_server_button_clicked)
        self.first_connect_button.connect("clicked", self.on_add_server_button_clicked)
        setting = Gio.Settings.new("org.ponderorg.UPSMonitor")
        setting.bind("run-in-background", self.run_in_background, "active", Gio.SettingsBindFlags.DEFAULT)
        thread = threading.Thread(target=self.update_profiles, daemon = True)
        thread.start()

    def on_add_server_button_clicked(self, widget):
        max_width = 600
        max_height = 680
        allocation = self.get_allocation()
        if allocation.width < max_width and allocation.height < max_height :
            self.add_server_box.set_default_size(allocation.width, allocation.height)
        elif allocation.width < max_width :
            self.add_server_box.set_default_size(allocation.width, max_height)
        elif allocation.height < max_height :
            self.add_server_box.set_default_size(max_width, allocation.height)
        else:
            self.add_server_box.set_default_size(max_width, max_height)
        self.add_server_box.present()

    def update_profiles(self, widget = None, host_var = None):
        if self.start_dbus_connection():
            self.update_temporary_profiles(widget, host_var)
            self.update_saved_profiles(widget, host_var)
        else:
            self.no_dbus_connection.set_visible(True)
            self.no_host_connection.set_visible(False)

    def start_dbus_connection(self):
        dbus_ready = False
        dbus_counter = 0
        if self.dbus_client == None :
            while not dbus_ready and dbus_counter < 10:
                try:
                    self.dbus_client = UPSMonitorClient()
                    self.dbus_client.connect_to_signal('host_updated', self.update_profiles)
                    self.dbus_client.connect_to_signal('host_deleated', self.delete_profile)
                    dbus_ready = True
                except dbus.exceptions.DBusException as e:
                    print('DBus daemo not ready: ', e)
                    dbus_counter += 1
                    time.sleep(1)
            return dbus_ready
        else:
            return True

    def update_temporary_profiles(self, widget = None, host_var = None):
        while self.temporary_profiles_list.get_last_child() != None:
            self.temporary_profiles_list.remove(self.temporary_profiles_list.get_last_child())
        host_list = self.dbus_client.get_all_temporary_hosts()
        if len(host_list) > 0:
            self.temporary_profiles_group.set_visible(True)
            self.no_host_connection.set_visible(False)
        else:
            self.temporary_profiles_group.set_visible(False)
        for host in host_list:
            action_row = self.create_action_row(host)
            self.temporary_profiles_list.append(action_row)

    def update_saved_profiles(self, widget = None, host_var = None):
        while self.saved_profiles_list.get_last_child() != None:
            self.saved_profiles_list.remove(self.saved_profiles_list.get_last_child())
        host_list = self.dbus_client.get_all_hosts()
        if len(host_list) > 0:
            self.saved_profiles_group.set_visible(True)
            self.no_host_connection.set_visible(False)
        else:
            self.saved_profiles_group.set_visible(False)
        for host in host_list:
            action_row = self.create_action_row(host)
            self.saved_profiles_list.append(action_row)

    def create_action_row(self, host:Host) -> Adw.ActionRow:
        action_row = Adw.ActionRow()
        if host.profile_name != None:
            action_row.set_title(host.profile_name)
            action_row.host = host
            action_row.set_subtitle(host.ip_address)
            next_image = Gtk.Image.new_from_icon_name("go-next-symbolic")
            action_row.add_suffix(next_image)
            action_row.set_activatable(True)
            action_row.connect("activated", self.on_clicked)
        else:
            action_row.set_title(host.ip_address)
        return action_row

    def cancel_row(self, widget):
        host_services = HostServices()
        host_services.delete_host(widget.host_data.host_id)
        self.update_profiles()

    def on_clicked(self, widget):
        new_page = HostPreferencesPage(host_data=widget.host, real_parent=self)
        self.push_subpage(new_page)

    def delete_profile(self):
        self.pop_subpage()
        self.update_profiles()

