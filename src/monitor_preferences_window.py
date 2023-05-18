from gi.repository import Adw
from gi.repository import Gtk

@Gtk.Template(resource_path='/org/ponderorg/UPSMonitor/monitor_preferences_window.ui')
class MonitorPreferencesWindow(Adw.PreferencesWindow):
    __gtype_name__ = 'MonitorPreferencesWindow'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
