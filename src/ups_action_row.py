from gi.repository import Adw
from gi.repository import Gtk

@Gtk.Template(resource_path='/org/ponderorg/UPSMonitor/ui/ups_action_row.ui')
class UpsActionRow(Adw.ActionRow):
    __gtype_name__ = 'UpsActionRow'

    row_image = Gtk.Template.Child()

    def __init__(self, **kwargs):
        ups_data = kwargs.get("ups_data", None)
        if ups_data != None:
            kwargs.pop("ups_data")
        super().__init__(**kwargs)
        self.ups_data = ups_data
        self.set_title(self.ups_data.name)
        if self.ups_data.host.profile_name != None:
            self.set_subtitle(self.ups_data.host.profile_name)
        else:
            self.set_subtitle(self.ups_data.host.ip_address)
        image_name = "battery-full-symbolic"
        if self.ups_data.ups["status"] == "OB":
            if int(self.ups_data.battery["charge"]) >= 90:
                image_name = "battery-full-symbolic"
            elif int(self.ups_data.battery["charge"]) >= 80:
                image_name = "battery-level-90-symbolic"
            elif int(self.ups_data.battery["charge"]) >= 70:
                image_name = "battery-level-70-symbolic"
            elif int(self.ups_data.battery["charge"]) >= 60:
                image_name = "battery-level-60-symbolic"
            elif int(self.ups_data.battery["charge"]) >= 50:
                image_name = "battery-level-50-symbolic"
            elif int(self.ups_data.battery["charge"]) >= 40:
                image_name = "battery-level-40-symbolic"
            elif int(self.ups_data.battery["charge"]) >= 30:
                image_name = "battery-level-30-symbolic"
            elif int(self.ups_data.battery["charge"]) >= 20:
                image_name = "battery-level-20-symbolic"
            elif int(self.ups_data.battery["charge"]) >= 10:
                image_name = "battery-leve-10-symbolic"
            else:
                image_name = "battery-level-0-symbolic"
        elif self.ups_data.ups["status"] == "OL":
            if int(self.ups_data.battery["charge"]) >= 90:
                image_name = "battery-full-charging-symbolic"
            elif int(self.ups_data.battery["charge"]) >= 80:
                image_name = "battery-level-90-charging-symbolic"
            elif int(self.ups_data.battery["charge"]) >= 70:
                image_name = "battery-level-70-charging-symbolic"
            elif int(self.ups_data.battery["charge"]) >= 60:
                image_name = "battery-level-60-charging-symbolic"
            elif int(self.ups_data.battery["charge"]) >= 50:
                image_name = "battery-level-50-charging-symbolic"
            elif int(self.ups_data.battery["charge"]) >= 40:
                image_name = "battery-level-40-charging-symbolic"
            elif int(self.ups_data.battery["charge"]) >= 30:
                image_name = "battery-level-30-charging-symbolic"
            elif int(self.ups_data.battery["charge"]) >= 20:
                image_name = "battery-level-20-charging-symbolic"
            elif int(self.ups_data.battery["charge"]) >= 10:
                image_name = "battery-level-10-charging-symbolic"
            else:
                image_name = "battery-level-0-charging-symbolic"
        self.row_image.set_from_icon_name(image_name)
