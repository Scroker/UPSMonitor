import threading
import time

from pynut3 import nut3

from gi.repository import Adw, Gtk, GLib, GObject

from .data_model import Host
from .service_model import HostServices, UPServices

@Gtk.Template(resource_path='/org/ponderorg/UPSMonitor/ui/add_new_server_box.ui')
class AddNewServerBox(Gtk.Box):
    __gtype_name__ = 'AddNewServerBox'

    ip_address = Gtk.Template.Child()
    progress = Gtk.Template.Child()
    username = Gtk.Template.Child()
    password = Gtk.Template.Child()
    connect_button = Gtk.Template.Child()
    cancel_button = Gtk.Template.Child()
    port = Gtk.Template.Child()
    banner = Gtk.Template.Child()
    profile_name = Gtk.Template.Child()
    profile_row  = Gtk.Template.Child()
    authentication_row = Gtk.Template.Child()

    @GObject.Signal(flags=GObject.SignalFlags.RUN_LAST, return_type=bool,
                    arg_types=(object,),
                    accumulator=GObject.signal_accumulator_true_handled)
    def conncetion_ok(self, *host):
        pass

    @GObject.Signal
    def cancel_connection(self):
        pass

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect_button.connect("clicked", self.do_connect)
        self.cancel_button.connect("clicked",self.cancel)
        self.port.set_text('3493')

    def cancel(self, widget):
        self.emit("cancel_connection")

    def do_connect(self, widget):
        self.progress.set_visible(True)
        thread = threading.Thread(target=self.load_function, daemon = True)
        thread.start()
        thread = threading.Thread(target=self._do_connect, daemon = True)
        thread.start()

    def close_banner(self):
        time.sleep(5)
        self.banner.set_revealed(False)

    def load_function(self):
        for i in range(50):
            GLib.idle_add(self.update_progess, i)
            time.sleep(0.2)

    def update_progess(self, i):
        self.progress.pulse()
        self.progress.set_text(str(i))
        return False

    def _do_connect(self):
        ip_address = self.ip_address.get_text()
        username = self.username.get_text()
        password = self.password.get_text()
        name = self.profile_name.get_text()
        try:
            port = int(self.port.get_text())
        except ValueError:
            self.banner.set_title("Port value not valid")
            self.banner.set_revealed(True)
            self.progress.set_visible(False)
            thread = threading.Thread(target=self.close_banner, daemon = True)
            thread.start()
            return
        if self.authentication_row.get_enable_expansion() and username != "" and password != "":
            host = Host(host_id=None, ip_address=ip_address, port=port, username=username, password=password)
        else:
            host = Host(host_id=None, ip_address=ip_address, port=port)
        try:
            upservices = UPServices(host)
        except nut3.PyNUT3Error:
            self.banner.set_title(_("Ops! Connection error, please retry.."))
            self.banner.set_revealed(True)
            self.progress.set_visible(False)
            thread = threading.Thread(target=self.close_banner, daemon = True)
            thread.start()
            return
        if self.profile_row.get_enable_expansion():
            try:
                if name == "" or name == None:
                    host.profile_name = host.ip_address
                else:
                    host.profile_name = name
                host_services = HostServices()
                host_services.save_host(host)
                host = host_services.get_host_by_name(host.profile_name)
            except Exception:
                self.banner.set_title(_("Profile name already exist"))
                self.banner.set_revealed(True)
                self.progress.set_visible(False)
                thread = threading.Thread(target=self.close_banner, daemon = True)
                thread.start()
                return
        self.emit("conncetion_ok", host)
        self.progress.set_visible(False)
