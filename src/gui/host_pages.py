from gi.repository import Adw, Gtk, GObject

from .ups_monitor_daemon import UPSMonitorClient

@Gtk.Template(resource_path='/org/ponderorg/UPSMonitor/ui/host_settings_page.ui')
class HostSettingsPage(Adw.NavigationPage):
    __gtype_name__ = 'HostSettingsPage'

    port_row = Gtk.Template.Child()
    username_row = Gtk.Template.Child()
    password_row = Gtk.Template.Child()
    ip_address_row = Gtk.Template.Child()
    save_button = Gtk.Template.Child()
    overlay = Gtk.Template.Child()
    authentication_switch = Gtk.Template.Child()

    def __init__(self, **kwargs):
        self.host_data = kwargs.get("host_data", None)
        if self.host_data != None:
            kwargs.pop("host_data")
        super().__init__(**kwargs)
        self.set_title('Connection settings')
        self.save_button.connect("clicked", self.on_save_host)
        if self.host_data != None:
            self.port_row.set_text(str(self.host_data.port))
            if self.host_data.password != None and self.host_data.username != None:
                self.username_row.set_text(self.host_data.username)
                self.password_row.set_text(self.host_data.password)
            self.ip_address_row.set_text(self.host_data.ip_address)

    def on_save_host(self, widget):
        self.host_data.ip_address = self.ip_address_row.get_text()
        self.host_data.port = self.port_row.get_text()
        if self.authentication_switch.get_active() and username != "" and password != "":
            self.host_data.username = self.username_row.get_text()
            self.host_data.password = self.password_row.get_text()
        else:
            self.host_data.username = None
            self.host_data.password = None
        UPSMonitorClient().update_host(self.host_data)
        saved_notification = Adw.Toast()
        saved_notification.set_title("Host modification saved!")
        saved_notification.set_timeout(2)
        self.overlay.add_toast(saved_notification)

@Gtk.Template(resource_path='/org/ponderorg/UPSMonitor/ui/host_informations_page.ui')
class HostInformationsPage(Adw.NavigationPage):
    __gtype_name__ = 'HostInformationsPage'

    overlay = Gtk.Template.Child()
    save_button = Gtk.Template.Child()
    delete_button = Gtk.Template.Child()
    server_name_row = Gtk.Template.Child()
    connection_settings_row = Gtk.Template.Child()
    devices_group = Gtk.Template.Child()

    def __init__(self, **kwargs):
        self.host_data = kwargs.get("host_data", None)
        if self.host_data != None:
            kwargs.pop("host_data")
        super().__init__(**kwargs)
        self.set_title('Host informations')
        self._dbus_client = UPSMonitorClient()
        self.delete_button.connect("clicked",self.on_delete_host)
        self.save_button.connect("clicked", self.on_save_host)
        for ups in self._dbus_client.get_ups_by_host(self.host_data.host_id):
            ups_row = Adw.ActionRow()
            ups_row.set_title(ups.ups_name)
            ups_row.add_prefix(Gtk.Image.new_from_icon_name('ups-symbolic'))
            self.devices_group.add(ups_row)
        if self.host_data != None:
            self.server_name_row.set_text(self.host_data.profile_name)

    def on_save_host(self, widget):
        self.host_data = self.host_data
        self.host_data.profile_name = self.server_name_row.get_text()
        self._dbus_client.update_host(self.host_data)
        saved_notification = Adw.Toast()
        saved_notification.set_title("Host modification saved!")
        saved_notification.set_timeout(2)
        self.overlay.add_toast(saved_notification)

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
            UPSMonitorClient().delete_host(self.host_data.host_id)
        elif response == Gtk.ResponseType.CANCEL:
            pass
        widget.destroy()
