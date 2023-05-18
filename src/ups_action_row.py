from gi.repository import Adw
from gi.repository import Gtk

@Gtk.Template(resource_path='/org/ponderorg/UPSMonitor/ups_action_row.ui')
class UpsActionRow(Adw.ActionRow):
    __gtype_name__ = 'UpsActionRow'

    def __init__(self, **kwargs):
        ups_data = kwargs.get("ups_data", None)
        if ups_data != None:
            kwargs.pop("ups_data")
        super().__init__(**kwargs)
        for k1, v1 in ups_data.items():
            self.set_title(v1)
            self.set_subtitle(k1)
