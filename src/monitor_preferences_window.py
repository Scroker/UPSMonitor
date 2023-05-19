from gi.repository import Adw
from gi.repository import Gtk

from .data_model import Host
from .service_model import HostServices

@Gtk.Template(resource_path='/org/ponderorg/UPSMonitor/monitor_preferences_window.ui')
class MonitorPreferencesWindow(Adw.PreferencesWindow):
    __gtype_name__ = 'MonitorPreferencesWindow'

    saved_profiles_group = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.host_services = HostServices()
        self.update_data()

    def update_data(self):
        for host in self.host_services.get_all_hosts():
            action_row = self.create_action_row(host)
            self.saved_profiles_group.add(action_row)

    def create_action_row(self, host:Host):
        cancel_button = self.create_cancel_button(host)
        action_row = Adw.ActionRow()
        action_row.set_title(host.ip_address)
        action_row.set_subtitle("Port: " + str(host.port))
        action_row.add_suffix(cancel_button)
        return action_row

    def create_cancel_button(self, host:Host):
        cancel_button = Gtk.Button()
        cancel_button.host_data = host
        cancel_button.set_icon_name("user-trash-symbolic")
        cancel_button.set_margin_top(10)
        cancel_button.set_margin_bottom(10)
        cancel_button.connect("clicked", self.cancel_row)
        return cancel_button

    def cancel_row(self, widget):
        host = widget.host_data
        self.host_services.delete_host(host.host_id)
        self.saved_profiles_group.remove(widget)
        
