from gi.repository import Adw
from gi.repository import Gtk

from .data_model import Host
from .service_model import HostServices
from .add_new_server_box import AddNewServerBox
from .host_preferences_page import HostPreferencesPage

@Gtk.Template(resource_path='/org/ponderorg/UPSMonitor/ui/monitor_preferences_window.ui')
class MonitorPreferencesWindow(Adw.PreferencesWindow):
    __gtype_name__ = 'MonitorPreferencesWindow'

    saved_profiles_list = Gtk.Template.Child()
    connect_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_data(None)
        self.connect_button.connect("clicked", self.on_add_server_button_clicked)

    def on_add_server_button_clicked(self, widget):
        max_width = 600
        max_height = 680
        allocation = self.get_allocation()
        add_server_box = AddNewServerBox()
        add_server_box.set_transient_for(self)
        add_server_box.set_modal(True)
        if allocation.width < max_width and allocation.height < max_height :
            add_server_box.set_default_size(allocation.width, allocation.height)
        elif allocation.width < max_width :
            add_server_box.set_default_size(allocation.width, max_height)
        elif allocation.height < max_height :
            add_server_box.set_default_size(max_width, allocation.height)
        else:
            add_server_box.set_default_size(max_width, max_height)
        add_server_box.connect("conncetion_ok", self.update_data)
        add_server_box.present()

    def update_data(self, widget):
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
        next_image = Gtk.Image.new_from_icon_name("go-next-symbolic")
        action_row.add_suffix(next_image)
        action_row.set_activatable(True)
        action_row.connect("activated", self.on_clicked)
        return action_row

    def cancel_row(self, widget):
        host_services = HostServices()
        host_services.delete_host(widget.host_data.host_id)
        self.update_data()        

    def on_clicked(self, widget):
        new_page = HostPreferencesPage(host_data=widget.host, real_parent=self)
        new_page.connect("host_saved", self.update_data)
        self.push_subpage(new_page)
