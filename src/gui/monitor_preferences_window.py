import threading, dbus, time, os

from gi.repository import Adw, Gtk, Gio, GObject, GLib

from .data_model import Host
from .add_new_server_box import AddNewServerBox
from .ups_monitor_daemon import UPSMonitorClient
from .host_pages import HostSettingsPage, HostInformationsPage

APPLICATION_ID = 'org.ponderorg.UPSMonitor'

@Gtk.Template(resource_path='/org/ponderorg/UPSMonitor/ui/monitor_preferences_window.ui')
class MonitorPreferencesWindow(Adw.PreferencesWindow):
    __gtype_name__ = 'MonitorPreferencesWindow'

    saved_profiles_list = Gtk.Template.Child()
    saved_profiles_group = Gtk.Template.Child()
    run_in_background = Gtk.Template.Child()
    run_at_boot = Gtk.Template.Child()
    temporary_profiles_list = Gtk.Template.Child()
    temporary_profiles_group = Gtk.Template.Child()
    no_host_connection = Gtk.Template.Child()
    no_dbus_connection = Gtk.Template.Child()
    add_temp_button = Gtk.Template.Child()
    dbus_client = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_server_box = AddNewServerBox()
        self.add_server_box.set_transient_for(self)
        self.add_server_box.set_modal(True)
        self.setting = Gio.Settings.new("org.ponderorg.UPSMonitor")
        self.setting.bind("run-in-background", self.run_in_background, "active", Gio.SettingsBindFlags.DEFAULT)
        self.setting.bind("run-at-boot", self.run_at_boot, "active", Gio.SettingsBindFlags.DEFAULT)
        thread = threading.Thread(target=self.update_profiles, daemon = True)
        thread.start()

    @Gtk.Template.Callback()
    def on_add_server_button_clicked(self, widget):
        allocation = self.get_allocation()
        self.add_server_box.present()

    def update_profiles(self, widget = None, host_var = None):
        if self.start_dbus_connection():
            self.no_dbus_connection.set_visible(False)
            self.no_host_connection.set_visible(True)
            self.add_temp_button.set_visible(True)
            self.update_temporary_profiles(widget, host_var)
            self.update_saved_profiles(widget, host_var)

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
            temporary_host_row = TemporaryHostActionRow(host_data=host, real_parent=self)
            self.temporary_profiles_list.append(temporary_host_row)

    def update_saved_profiles(self, widget = None, host_var = None):
        while self.saved_profiles_list.get_last_child() != None:
            self.saved_profiles_list.remove(self.saved_profiles_list.get_last_child())
        host_list = self.dbus_client.get_all_hosts()
        if len(host_list) > 0:
            self.add_temp_button.set_visible(False)
            self.saved_profiles_group.set_visible(True)
            self.no_host_connection.set_visible(False)
        else:
            self.saved_profiles_group.set_visible(False)
        for host in host_list:
            saved_host_row = SavedHostActionRow(host_data=host)
            saved_host_row.connect("activated", self.on_saved_row_clicked, host)
            self.saved_profiles_list.append(saved_host_row)

    def on_saved_row_clicked(self, widget, args):
        new_page = HostInformationsPage(host_data=args, real_parent=self)
        new_page.connection_settings_row.connect("activated", self.on_connection_row_clicked, args)
        self.push_subpage(new_page)

    def on_connection_row_clicked(self, widget, args):
        new_page = HostSettingsPage(host_data=args)
        self.push_subpage(new_page)

    def delete_profile(self):
        self.pop_subpage()
        self.update_profiles()

    @Gtk.Template.Callback()
    def run_background_switch_selected(self, widget, args):
        if self.setting.get_value("run-in-background") :
            self.run_at_boot.set_active(False)

    @Gtk.Template.Callback()
    def autostart_switch_selected(self, widget, args):
        if not self.setting.get_value("run-at-boot") :
            self.run_in_background.set_active(True)


@Gtk.Template(resource_path='/org/ponderorg/UPSMonitor/ui/saved_host_action_row.ui')
class SavedHostActionRow(Adw.ActionRow):
    __gtype_name__ = 'SavedHostActionRow'

    def __init__(self, **kwargs):
        self.host =  kwargs.get("host_data", None)
        if self.host != None:
            kwargs.pop("host_data")
        super().__init__(**kwargs)
        self.set_title(self.host.profile_name)
        self.set_subtitle(self.host.ip_address)
        self.set_activatable(True)


@Gtk.Template(resource_path='/org/ponderorg/UPSMonitor/ui/temporary_host_action_row.ui')
class TemporaryHostActionRow(Adw.ActionRow):
    __gtype_name__ = 'TemporaryHostActionRow'

    delete_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        self.real_parent = kwargs.get("real_parent", None)
        self.host = kwargs.get("host_data", None)
        if self.host != None:
            kwargs.pop("host_data")
        if self.real_parent != None:
            kwargs.pop("real_parent")
        super().__init__(**kwargs)
        self.set_title(self.host.ip_address)
        self.delete_button.connect("clicked",self.on_delete_host)

    def on_delete_host(self, widget):
        dialog = Gtk.MessageDialog(
            transient_for=self.real_parent,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text="Deleating Host",
            secondary_text="Are you sure to delete this Host?"
        )
        dialog.set_modal(True)
        dialog.connect("response", self._delete_host)
        dialog.present()

    def _delete_host(self, widget, response):
        if response == Gtk.ResponseType.OK:
            UPSMonitorClient().delete_temporary_host(self.host.ip_address)
        elif response == Gtk.ResponseType.CANCEL:
            pass
        widget.destroy()
        
