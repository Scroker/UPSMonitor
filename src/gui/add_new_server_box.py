import threading, time

from pynut3 import nut3

from gi.repository import Adw, Gtk, GLib, GObject

from .data_model import Host
from .exception_model import HostNameAlreadyExist, HostAddressAlreadyExist
from .ups_monitor_daemon import UPSMonitorClient

@Gtk.Template(resource_path='/org/ponderorg/UPSMonitor/ui/add_new_server_box.ui')
class AddNewServerBox(Adw.Window):
    __gtype_name__ = 'AddNewServerBox'

    port = Gtk.Template.Child()
    banner = Gtk.Template.Child()
    progress = Gtk.Template.Child()
    username = Gtk.Template.Child()
    password = Gtk.Template.Child()
    ip_address = Gtk.Template.Child()
    profile_name = Gtk.Template.Child()
    cancel_button = Gtk.Template.Child()
    connect_button = Gtk.Template.Child()
    save_profile_switch = Gtk.Template.Child()
    authentication_switch = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect_button.connect("clicked", self.do_connect)
        self.cancel_button.connect("clicked",self.cancel)

    def cancel(self, widget):
        self.hide()

    def do_connect(self, widget):
        self.progress.set_visible(True)
        connect_thread = threading.Thread(target=self._do_connect, daemon = True)
        connect_thread.start()
        load_thread = threading.Thread(target=self.load_function, daemon = True)
        load_thread.start()

    def close_banner(self):
        time.sleep(5)
        self.banner.set_revealed(False)

    def load_function(self):
        for i in range(50):
            GLib.idle_add(self.update_progess, i)
            time.sleep(0.2)
        self.progress.set_visible(False)

    def update_progess(self, i):
        self.progress.pulse()
        self.progress.set_text(str(i))
        return False

    def _do_connect(self):
        self.banner.set_revealed(False)
        ip_address = self.ip_address.get_text()
        username = self.username.get_text()
        password = self.password.get_text()
        profile_name = self.profile_name.get_text()
        ups_monitor_client = UPSMonitorClient()
        if ip_address == "":
            self.banner.set_title("Host address should not be null")
            self.banner.set_revealed(True)
            self.progress.set_visible(False)
            thread = threading.Thread(target=self.close_banner, daemon = True)
            thread.start()
            return
        try:
            port = int(self.port.get_text())
        except ValueError:
            self.banner.set_title("Not valid port number")
            self.banner.set_revealed(True)
            self.progress.set_visible(False)
            thread = threading.Thread(target=self.close_banner, daemon = True)
            thread.start()
            return
        if self.authentication_switch.get_active() and username != "" and password != "":
            host = Host(host_id=None, ip_address=ip_address, port=port, username=username, password=password)
        else:
            host = Host(host_id=None, ip_address=ip_address, port=port)
        if self.save_profile_switch.get_active():
            try:
                if profile_name == "" or profile_name == None:
                    host.profile_name = host.ip_address
                else:
                    host.profile_name = profile_name
                ups_monitor_client.save_host(host)
                print('Saved host: ', vars(host))
                host = ups_monitor_client.get_host_by_name(profile_name)
                print('Retrived host: ', vars(host))
                self.hide()
            except HostNameAlreadyExist :
                self.banner.set_title(_("Profile name already exist"))
                self.banner.set_revealed(True)
                self.progress.set_visible(False)
                thread = threading.Thread(target=self.close_banner, daemon = True)
                thread.start()
                return
            except HostAddressAlreadyExist :
                self.banner.set_title(_("Host address name already exist"))
                self.banner.set_revealed(True)
                self.progress.set_visible(False)
                thread = threading.Thread(target=self.close_banner, daemon = True)
                thread.start()
                return
            except Exception as e :
                print(e)
                self.banner.set_title(_("Unexpected error!"))
                self.banner.set_revealed(True)
                self.progress.set_visible(False)
                thread = threading.Thread(target=self.close_banner, daemon = True)
                thread.start()
                return
        if not ups_monitor_client.host_connection(host):
            self.banner.set_title(_("Ops! Connection error, please retry.."))
            self.banner.set_revealed(True)
            self.progress.set_visible(False)
            thread = threading.Thread(target=self.close_banner, daemon = True)
            thread.start()
            return
        self.progress.set_visible(False)
        self.hide()

