import threading, dbus, time, os, logging, subprocess

from gi.repository import Adw, Gtk, Gio, GObject, GLib

from .data_model import Host
from .add_new_server_box import AddNewServerBox
from .ups_monitor_daemon import UPSMonitorClient
from .nut_controller import NutController
from .host_pages import HostSettingsPage, HostInformationsPage

APPLICATION_ID = 'org.ponderorg.UPSMonitor'
LOG_LEVEL = logging.ERROR

@Gtk.Template(resource_path='/org/ponderorg/UPSMonitor/ui/monitor_preferences_window.ui')
class MonitorPreferencesWindow(Adw.PreferencesWindow):
    __gtype_name__ = 'MonitorPreferencesWindow'

    saved_profiles_list = Gtk.Template.Child()
    saved_profiles_group = Gtk.Template.Child()
    run_in_background = Gtk.Template.Child()
    run_at_boot = Gtk.Template.Child()
    dark_theme_row = Gtk.Template.Child()
    refresh_interval_row = Gtk.Template.Child()
    max_retry_row = Gtk.Template.Child()
    temporary_profiles_list = Gtk.Template.Child()
    temporary_profiles_group = Gtk.Template.Child()
    no_host_connection = Gtk.Template.Child()
    no_dbus_connection = Gtk.Template.Child()
    add_temp_button = Gtk.Template.Child()
    installed_nut_row = Gtk.Template.Child()
    install_nut_row = Gtk.Template.Child()
    installed_nut_label = Gtk.Template.Child()
    dbus_client = None

    def __init__(self, **kwargs):
        self.style_manager = kwargs.get("style_manager", None)
        if self.style_manager != None:
            kwargs.pop("style_manager")
        super().__init__(**kwargs)
        self.add_server_box = AddNewServerBox()
        self.add_server_box.set_transient_for(self)
        self.add_server_box.set_modal(True)
        self._settings = Gio.Settings.new(APPLICATION_ID)
        self._settings.bind("run-in-background", self.run_in_background, "active", Gio.SettingsBindFlags.DEFAULT)
        self._settings.bind("run-at-boot", self.run_at_boot, "active", Gio.SettingsBindFlags.DEFAULT)
        self._settings.bind("prefer-dark", self.dark_theme_row, "active", Gio.SettingsBindFlags.DEFAULT)
        self._settings.bind("retry-max", self.max_retry_row, "value", Gio.SettingsBindFlags.DEFAULT)
        self._settings.bind("polling-interval", self.refresh_interval_row, "value", Gio.SettingsBindFlags.DEFAULT)
        self.initialize_logs()
        thread = threading.Thread(target=self.update_profiles, daemon = True)
        thread.start()
        thread = threading.Thread(target=self.nut_check_install, daemon = True)
        thread.start()

    def nut_check_install(self):
        installed = NutController.nut_check_install()
        if installed != None :
            self.installed_nut_row.set_visible(True)
            self.install_nut_row.set_visible(False)
            self.installed_nut_label.set_label(installed['version'])
        else:
            self.installed_nut_row.set_visible(False)
            self.install_nut_row.set_visible(True)

    def install_nut(self):
        NutController.install_nut()
        self.nut_check_install()

    @Gtk.Template.Callback()
    def install_nut_selected(self, widget):
        thread = threading.Thread(target=self.install_nut, daemon = True)
        thread.start()

    def initialize_logs(self):
        self._logger = logging.getLogger('MonitorPreferencesWindow')
        c_handler = logging.FileHandler('.var/app/' + APPLICATION_ID + '/data/SystemOut_gui.log')
        c_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self._logger.setLevel(LOG_LEVEL)
        self._logger.addHandler(c_handler)

    def update_profiles(self, widget = None, host_var = None):
        if self.start_dbus_connection():
            self.no_dbus_connection.set_visible(False)
            self.no_host_connection.set_visible(True)
            self.add_temp_button.set_visible(True)
            self.update_temporary_profiles(widget, host_var)
            self.update_saved_profiles(widget, host_var)

    def start_dbus_connection(self):
        dbus_ready = False
        if self.dbus_client == None :
            dbus_counter = 0
            while dbus_counter < 10:
                try:
                    self.dbus_client = UPSMonitorClient()
                    self.dbus_client.connect_to_signal('host_updated', self.update_profiles)
                    self.dbus_client.connect_to_signal('host_deleated', self.delete_profile)
                    self._logger.info("comunication daemon ready")
                    dbus_ready = True
                    break
                except dbus.exceptions.DBusException as e:
                    dbus_counter += 1
                    if dbus_counter == 10:
                        self.logger.exception('deamon not ready, max retry reached!', e)
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
    def on_add_server_button_clicked(self, widget):
        allocation = self.get_allocation()
        self.add_server_box.present()

    @Gtk.Template.Callback()
    def run_background_switch_selected(self, widget, args):
        if self._settings.get_value("run-in-background") :
            self.run_at_boot.set_active(False)

    @Gtk.Template.Callback()
    def autostart_switch_selected(self, widget, args):
        if not self._settings.get_value("run-at-boot") :
            self.run_in_background.set_active(True)

    @Gtk.Template.Callback()
    def dark_theme_selected(self, widget, args):
        if self.dark_theme_row.get_active() :
            self.style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        elif not self.dark_theme_row.get_active() :
            self.style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)


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
        
