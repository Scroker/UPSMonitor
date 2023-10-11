from gi.repository import Adw, Gtk, GObject

from .ups_monitor_daemon import UPSMonitorClient

@Gtk.Template(resource_path='/org/ponderorg/UPSMonitor/ui/host_preferences_page.ui')
class HostPreferencesPage(Adw.NavigationPage):
    __gtype_name__ = 'HostPreferencesPage'

    port_row = Gtk.Template.Child()
    username_row = Gtk.Template.Child()
    server_name_row = Gtk.Template.Child()
    password_row = Gtk.Template.Child()
    ip_address_row = Gtk.Template.Child()
    save_button = Gtk.Template.Child()
    delete_button = Gtk.Template.Child()
    overlay = Gtk.Template.Child()

    @GObject.Signal
    def host_saved(self):
        pass

    def __init__(self, **kwargs):
        host_data = kwargs.get("host_data", None)
        real_parent = kwargs.get("real_parent", None)
        self.real_parent = real_parent
        self.host_data = host_data
        if host_data != None:
            kwargs.pop("host_data")
        if real_parent != None:
            kwargs.pop("real_parent")
        super().__init__(**kwargs)
        self.save_button.connect("clicked", self.on_save_host)
        self.delete_button.connect("clicked",self.on_delete_host)
        if host_data != None:
            self.port_row.set_text(str(host_data.port))
            if host_data.password != None and host_data.username != None:
                self.username_row.set_text(host_data.username)
                self.password_row.set_text(host_data.password)
            self.server_name_row.set_text(host_data.profile_name)
            self.ip_address_row.set_text(host_data.ip_address)

    def on_save_host(self, widget):
        host = self.host_data
        host.profile_name = self.server_name_row.get_text()
        host.ip_address = self.ip_address_row.get_text()
        host.port = self.port_row.get_text()
        host.username = self.username_row.get_text()
        host.password = self.password_row.get_text()
        UPSMonitorClient().update_host(host)
        saved_notification = Adw.Toast()
        saved_notification.set_title("Host modification saved!")
        saved_notification.set_timeout(2)
        self.overlay.add_toast(saved_notification)
        self.emit("host_saved")


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
            child = self.ups_page_leaflet.get_last_child()
            if isinstance(child, Adw.PreferencesPage):
                UPSMonitorClient().delete_host(child.host_data.host_id)
                self.hosts.remove(child.host_data)
                self.ups_page_leaflet.remove(child)
                if self.show_servers_button.get_active():
                    self.update_host_row()
                else:
                    for element in self.ups_list_box:
                        self.ups_list_box.remove(element)
                    thread = threading.Thread(target=self.refresh_ups_data, daemon = True)
                    thread.start()
                self.content_window_title.set_title("")
                self.content_window_title.set_subtitle("")
                self.leaflet.navigate(Adw.NavigationDirection.BACK)
        elif response == Gtk.ResponseType.CANCEL:
            pass
        widget.destroy()
