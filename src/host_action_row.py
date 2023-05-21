from gi.repository import Adw
from gi.repository import Gtk

@Gtk.Template(resource_path='/org/ponderorg/UPSMonitor/ui/host_action_row.ui')
class HostActionRow(Adw.ActionRow):
    __gtype_name__ = 'HostActionRow'

    def __init__(self, **kwargs):
        host_data = kwargs.get("host_data", None)
        if host_data != None:
            kwargs.pop("host_data")
        super().__init__(**kwargs)
        self.host_data = host_data
        self.set_title(self.host_data.profile_name)
        self.set_subtitle(self.host_data.ip_address)
