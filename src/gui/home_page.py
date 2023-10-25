from gi.repository import Adw, Gtk

from .data_model import UPS
from .ups_monitor_daemon import UPSMonitorClient, NotificationType

@Gtk.Template(resource_path='/org/ponderorg/UPSMonitor/ui/home_page.ui')
class HomePage(Adw.NavigationPage):
    __gtype_name__ = 'HomePage'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
