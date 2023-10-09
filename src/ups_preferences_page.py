from gi.repository import Adw
from gi.repository import Gtk

@Gtk.Template(resource_path='/org/ponderorg/UPSMonitor/ui/ups_preferences_page.ui')
class UpsPreferencesPage(Adw.PreferencesPage):
    __gtype_name__ = 'UpsPreferencesPage'

    bettery_group = Gtk.Template.Child()
    device_group = Gtk.Template.Child()
    driver_group = Gtk.Template.Child()
    input_group = Gtk.Template.Child()
    output_group = Gtk.Template.Child()
    ups_group = Gtk.Template.Child()

    def __init__(self, **kwargs):
        ups_data = kwargs.get("ups_data", None)
        if ups_data != None:
            kwargs.pop("ups_data")
        super().__init__(**kwargs)
        if ups_data != None:
            self.set_title(ups_data.ups_name)
            for k2 in ups_data.battery:
                v2 = ups_data.battery[k2]
                action_row = Adw.ActionRow()
                action_row.set_title(_(k2))
                if "charge" in k2:
                    action_row.set_subtitle(v2+"%")
                    progress = Gtk.ProgressBar(fraction=int(v2)/100)
                    progress.set_margin_top(20)
                    action_row.add_suffix(progress)
                else:
                    action_row.add_suffix(Gtk.Label(label=v2))
                self.bettery_group.add(action_row)
            for k2 in ups_data.device:
                v2 = ups_data.device[k2]
                action_row = self.create_action_row(k2,v2)
                self.device_group.add(action_row)
            for k2 in ups_data.driver:
                v2 = ups_data.driver[k2]
                action_row = self.create_action_row(k2,v2)
                self.driver_group.add(action_row)
            for k2 in ups_data.input:
                v2 = ups_data.input[k2]
                action_row = self.create_action_row(k2,v2)
                self.input_group.add(action_row)
            for k2 in ups_data.output:
                v2 = ups_data.output[k2]
                action_row = self.create_action_row(k2,v2)
                self.output_group.add(action_row)
            for k2 in ups_data.ups:
                v2 = ups_data.ups[k2]
                action_row = self.create_action_row(k2,v2)
                self.ups_group.add(action_row)

    def create_action_row(self, title:str, value:str):
        action_row = Adw.ActionRow()
        action_row.set_title(_(title))
        action_row.add_suffix(Gtk.Label(label=value))
        return action_row
