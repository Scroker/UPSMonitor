from gi.repository import Adw
from gi.repository import Gtk

from .data_model import Host
from .service_model import HostServices
from .host_preferences_page import HostPreferencesPage

@Gtk.Template(resource_path='/org/ponderorg/UPSMonitor/ui/monitor_preferences_window.ui')
class MonitorPreferencesWindow(Adw.PreferencesWindow):
    __gtype_name__ = 'MonitorPreferencesWindow'

    saved_profiles_list = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_data()

    def update_data(self):
        while self.saved_profiles_list.get_last_child() != None:
            self.saved_profiles_list.remove(self.saved_profiles_list.get_last_child())
        host_services = HostServices()
        host_list = host_services.get_all_hosts()
        if len(host_list) > 0:
            self.saved_profiles_list.set_visible(True)
        else:
            self.saved_profiles_list.set_visible(False)
        for host in host_list:
            action_row = self.create_action_row(host)
            self.saved_profiles_list.append(action_row)


    def create_action_row(self, host:Host) -> Adw.ActionRow:
        action_row = Adw.ActionRow()
        action_row.host = host
        action_row.set_title(host.profile_name)
        action_row.set_subtitle(host.ip_address)
        action_row.set_activatable(True)
        action_row.connect("activated", self.on_clicked)
        return action_row

    def cancel_row(self, widget):
        host_services = HostServices()
        host_services.delete_host(widget.host_data.host_id)
        self.update_data()        

    def on_clicked(self, widget):
        new_page = HostPreferencesPage(host_data=widget.host)
        self.push_subpage(new_page)
