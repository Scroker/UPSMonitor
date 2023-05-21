from gi.repository import Adw
from gi.repository import Gtk

@Gtk.Template(resource_path='/org/ponderorg/UPSMonitor/ui/host_preferences_page.ui')
class HostPreferencesPage(Adw.PreferencesPage):
    __gtype_name__ = 'HostPreferencesPage'

    port_row = Gtk.Template.Child()
    username_row = Gtk.Template.Child()
    server_name_row = Gtk.Template.Child()
    password_row = Gtk.Template.Child()
    ip_address_row = Gtk.Template.Child()

    def __init__(self, **kwargs):
        host_data = kwargs.get("host_data", None)
        self.host_data = host_data
        if host_data != None:
            kwargs.pop("host_data")
        super().__init__(**kwargs)
        if host_data != None:
            self.port_row.set_text(str(host_data.port))
            if host_data.password != None and host_data.username != None:
                self.username_row.set_text(host_data.username)
                self.password_row.set_text(host_data.password)
            self.server_name_row.set_text(host_data.profile_name)
            self.ip_address_row.set_text(host_data.ip_address)
