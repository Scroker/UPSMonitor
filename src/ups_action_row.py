from gi.repository import Adw
from gi.repository import Gtk

@Gtk.Template(resource_path='/org/ponderorg/UPSMonitor/ui/ups_action_row.ui')
class UpsActionRow(Adw.ActionRow):
    __gtype_name__ = 'UpsActionRow'

    def __init__(self, **kwargs):
        ups_data = kwargs.get("ups_data", None)
        if ups_data != None:
            kwargs.pop("ups_data")
        super().__init__(**kwargs)
        self.ups_data = ups_data
        self.set_title(self.ups_data.name)
        self.set_subtitle(self.ups_data.key)
